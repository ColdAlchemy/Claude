// Celular Mouse - servidor.
// Roda no PC: serve a pagina do celular (HTTP) e recebe os movimentos (WebSocket).
// Compilado na hora pelo PowerShell (Add-Type). Windows PowerShell 5.1 usa C# 5:
// nada de interpolacao de string, "?." ou membros com "=>".
//
// Protocolo (mensagens binarias, inteiros little-endian):
//   0x01 dx:int16 dy:int16            mover o cursor (relativo)
//   0x02 botao:byte estado:byte       botao 0=esq 1=dir 2=meio; estado 1=baixo 0=cima
//   0x03 vertical:int16 horiz:int16   rolagem (120 = 1 "clique" da roda; + = para cima/direita)
//   0x05 id:uint32                    ping; o servidor devolve a mesma mensagem

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;

namespace CelularMouse
{
    public interface IMouse
    {
        void Move(int dx, int dy);
        void Button(int button, bool down);
        void Scroll(int vertical, int horizontal);
    }

    // Mouse real do Windows, via SendInput (a forma mais rapida de injetar entrada).
    public class WindowsMouse : IMouse
    {
        [StructLayout(LayoutKind.Sequential)]
        struct MOUSEINPUT
        {
            public int dx;
            public int dy;
            public uint mouseData;
            public uint dwFlags;
            public uint time;
            public IntPtr dwExtraInfo;
        }

        [StructLayout(LayoutKind.Sequential)]
        struct INPUT
        {
            public uint type; // 0 = INPUT_MOUSE
            public MOUSEINPUT mi;
        }

        [DllImport("user32.dll", SetLastError = true)]
        static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

        const uint MOVE = 0x0001;
        const uint LEFTDOWN = 0x0002, LEFTUP = 0x0004;
        const uint RIGHTDOWN = 0x0008, RIGHTUP = 0x0010;
        const uint MIDDLEDOWN = 0x0020, MIDDLEUP = 0x0040;
        const uint WHEEL = 0x0800, HWHEEL = 0x1000;

        static readonly int Size = Marshal.SizeOf(typeof(INPUT));

        static INPUT Make(uint flags, int dx, int dy, int data)
        {
            INPUT i = new INPUT();
            i.type = 0;
            i.mi.dx = dx;
            i.mi.dy = dy;
            i.mi.mouseData = unchecked((uint)data);
            i.mi.dwFlags = flags;
            return i;
        }

        public void Move(int dx, int dy)
        {
            SendInput(1, new INPUT[] { Make(MOVE, dx, dy, 0) }, Size);
        }

        public void Button(int button, bool down)
        {
            uint f;
            if (button == 0) f = down ? LEFTDOWN : LEFTUP;
            else if (button == 1) f = down ? RIGHTDOWN : RIGHTUP;
            else f = down ? MIDDLEDOWN : MIDDLEUP;
            SendInput(1, new INPUT[] { Make(f, 0, 0, 0) }, Size);
        }

        public void Scroll(int vertical, int horizontal)
        {
            List<INPUT> l = new List<INPUT>();
            if (vertical != 0) l.Add(Make(WHEEL, 0, 0, vertical));
            if (horizontal != 0) l.Add(Make(HWHEEL, 0, 0, horizontal));
            if (l.Count > 0) SendInput((uint)l.Count, l.ToArray(), Size);
        }
    }

    // Usado para testar fora do Windows: so escreve o que faria.
    public class LogMouse : IMouse
    {
        public void Move(int dx, int dy) { Console.WriteLine("[mouse] move " + dx + "," + dy); }
        public void Button(int button, bool down) { Console.WriteLine("[mouse] botao " + button + (down ? " baixo" : " cima")); }
        public void Scroll(int v, int h) { Console.WriteLine("[mouse] rolar v=" + v + " h=" + h); }
    }

    public class Servidor
    {
        const string WsGuid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";

        readonly string webDir;
        readonly string token;
        readonly IMouse mouse;
        int porta;
        int clientes;

        public Servidor(string webDir, string token, IMouse mouse, int porta)
        {
            this.webDir = webDir;
            this.token = token;
            this.mouse = mouse;
            this.porta = porta;
        }

        public int Porta { get { return porta; } }

        // ---------- rede local ----------

        public class Endereco
        {
            public string Nome;
            public string Ip;
            public bool TemGateway;
        }

        public static List<Endereco> EnderecosLocais()
        {
            List<Endereco> lista = new List<Endereco>();
            string[] virtuais = { "virtual", "vmware", "vbox", "hyper-v", "vethernet", "wsl", "docker", "loopback", "pseudo", "bluetooth" };
            try
            {
                foreach (NetworkInterface ni in NetworkInterface.GetAllNetworkInterfaces())
                {
                    if (ni.OperationalStatus != OperationalStatus.Up) continue;
                    if (ni.NetworkInterfaceType == NetworkInterfaceType.Loopback) continue;
                    if (ni.NetworkInterfaceType == NetworkInterfaceType.Tunnel) continue;
                    string desc = (ni.Name + " " + ni.Description).ToLower();
                    bool pular = false;
                    foreach (string v in virtuais) { if (desc.Contains(v)) { pular = true; break; } }
                    if (pular) continue;

                    IPInterfaceProperties props = ni.GetIPProperties();
                    bool gw = false;
                    foreach (GatewayIPAddressInformation g in props.GatewayAddresses)
                    {
                        if (g.Address.AddressFamily == AddressFamily.InterNetwork && !g.Address.Equals(IPAddress.Any)) gw = true;
                    }
                    foreach (UnicastIPAddressInformation u in props.UnicastAddresses)
                    {
                        if (u.Address.AddressFamily != AddressFamily.InterNetwork) continue;
                        string ip = u.Address.ToString();
                        if (ip.StartsWith("169.254.") || ip.StartsWith("127.")) continue;
                        Endereco e = new Endereco();
                        e.Nome = ni.Name;
                        e.Ip = ip;
                        e.TemGateway = gw;
                        lista.Add(e);
                    }
                }
            }
            catch (Exception) { }
            // Quem tem gateway (a rede de verdade) vem primeiro.
            lista.Sort(delegate (Endereco a, Endereco b) { return b.TemGateway.CompareTo(a.TemGateway); });
            return lista;
        }

        // ---------- laco principal ----------

        public void Rodar()
        {
            TcpListener listener = null;
            for (int p = porta; p < porta + 10; p++)
            {
                try
                {
                    listener = new TcpListener(IPAddress.Any, p);
                    listener.Start(16);
                    porta = p;
                    break;
                }
                catch (SocketException) { listener = null; }
            }
            if (listener == null) throw new Exception("Nao consegui abrir nenhuma porta entre " + porta + " e " + (porta + 9) + ".");

            while (true)
            {
                TcpClient c;
                try { c = listener.AcceptTcpClient(); }
                catch (Exception) { break; }
                Thread t = new Thread(delegate () { Atender(c); });
                t.IsBackground = true;
                t.Start();
            }
        }

        // ---------- HTTP ----------

        static byte[] LerCabecalho(NetworkStream s)
        {
            MemoryStream ms = new MemoryStream();
            byte[] b = new byte[2048];
            while (ms.Length < 16384)
            {
                int n = s.Read(b, 0, b.Length);
                if (n <= 0) return null;
                ms.Write(b, 0, n);
                byte[] all = ms.GetBuffer();
                int len = (int)ms.Length;
                for (int i = 3; i < len; i++)
                {
                    if (all[i] == 10 && all[i - 1] == 13 && all[i - 2] == 10 && all[i - 3] == 13)
                    {
                        byte[] r = new byte[i + 1];
                        Array.Copy(all, r, i + 1);
                        return r;
                    }
                }
            }
            return null;
        }

        static void Responder(NetworkStream s, int codigo, string status, string tipo, byte[] corpo)
        {
            string cab = "HTTP/1.1 " + codigo + " " + status + "\r\n" +
                "Content-Type: " + tipo + "\r\n" +
                "Content-Length: " + corpo.Length + "\r\n" +
                "Cache-Control: no-store\r\n" +
                "Connection: close\r\n\r\n";
            byte[] h = Encoding.ASCII.GetBytes(cab);
            s.Write(h, 0, h.Length);
            s.Write(corpo, 0, corpo.Length);
        }

        static void Texto(NetworkStream s, int codigo, string status, string msg)
        {
            Responder(s, codigo, status, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes(msg));
        }

        static string Json(string s)
        {
            return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }

        string InfoJson()
        {
            StringBuilder sb = new StringBuilder();
            sb.Append("{\"porta\":").Append(porta);
            sb.Append(",\"token\":").Append(Json(token));
            sb.Append(",\"clientes\":").Append(clientes);
            sb.Append(",\"enderecos\":[");
            bool primeiro = true;
            foreach (Endereco e in EnderecosLocais())
            {
                if (!primeiro) sb.Append(",");
                primeiro = false;
                sb.Append("{\"nome\":").Append(Json(e.Nome)).Append(",\"ip\":").Append(Json(e.Ip)).Append("}");
            }
            sb.Append("]}");
            return sb.ToString();
        }

        void Arquivo(NetworkStream s, string nome, string tipo)
        {
            string caminho = Path.Combine(webDir, nome);
            if (!File.Exists(caminho)) { Texto(s, 404, "Not Found", "Arquivo nao encontrado: " + nome); return; }
            Responder(s, 200, "OK", tipo, File.ReadAllBytes(caminho));
        }

        void Atender(TcpClient c)
        {
            string remoto = "?";
            bool contou = false;
            bool[] segurando = new bool[3];
            try
            {
                c.NoDelay = true; // sem espera de Nagle: menor latencia
                c.ReceiveTimeout = 5000;
                IPEndPoint ep = (IPEndPoint)c.Client.RemoteEndPoint;
                remoto = ep.Address.ToString();
                bool local = IPAddress.IsLoopback(ep.Address);
                NetworkStream s = c.GetStream();

                byte[] raw = LerCabecalho(s);
                if (raw == null) return;
                string[] linhas = Encoding.ASCII.GetString(raw).Split(new string[] { "\r\n" }, StringSplitOptions.RemoveEmptyEntries);
                string[] req = linhas[0].Split(' ');
                if (req.Length < 2 || req[0] != "GET") { Texto(s, 405, "Method Not Allowed", "Metodo nao permitido"); return; }

                Dictionary<string, string> cab = new Dictionary<string, string>();
                for (int i = 1; i < linhas.Length; i++)
                {
                    int k = linhas[i].IndexOf(':');
                    if (k > 0) cab[linhas[i].Substring(0, k).Trim().ToLower()] = linhas[i].Substring(k + 1).Trim();
                }

                string alvo = req[1];
                string caminho = alvo, query = "";
                int q = alvo.IndexOf('?');
                if (q >= 0) { caminho = alvo.Substring(0, q); query = alvo.Substring(q + 1); }

                if (caminho == "/ws")
                {
                    string t = ValorQuery(query, "t");
                    string key;
                    bool upgrade = cab.ContainsKey("upgrade") && cab["upgrade"].ToLower() == "websocket" && cab.TryGetValue("sec-websocket-key", out key);
                    if (!upgrade) { Texto(s, 400, "Bad Request", "Use WebSocket."); return; }
                    if (t != token) { Texto(s, 403, "Forbidden", "Token invalido."); return; }
                    key = cab["sec-websocket-key"];
                    string aceite = Convert.ToBase64String(SHA1.Create().ComputeHash(Encoding.ASCII.GetBytes(key + WsGuid)));
                    string resp = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + aceite + "\r\n\r\n";
                    byte[] rb = Encoding.ASCII.GetBytes(resp);
                    s.Write(rb, 0, rb.Length);

                    contou = true;
                    Interlocked.Increment(ref clientes);
                    Console.WriteLine("  Celular conectado: " + remoto);
                    // O celular manda um ping por segundo; 6 s de silencio = conexao morta.
                    c.ReceiveTimeout = 6000;
                    LacoWebSocket(s, segurando);
                    return;
                }

                if (caminho == "/") Arquivo(s, "index.html", "text/html; charset=utf-8");
                else if (caminho == "/qrcode.js") Arquivo(s, "qrcode.js", "application/javascript; charset=utf-8");
                else if (caminho == "/qr" || caminho == "/info")
                {
                    // Contem o token: so o proprio PC pode ver.
                    if (!local) { Texto(s, 403, "Forbidden", "Somente neste computador."); return; }
                    if (caminho == "/qr") Arquivo(s, "qr.html", "text/html; charset=utf-8");
                    else Responder(s, 200, "OK", "application/json; charset=utf-8", Encoding.UTF8.GetBytes(InfoJson()));
                }
                else Texto(s, 404, "Not Found", "Nao encontrado");
            }
            catch (Exception) { }
            finally
            {
                // Se o celular sumiu com um botao apertado, solta (evita mouse "preso").
                for (int b = 0; b < 3; b++) { if (segurando[b]) { try { mouse.Button(b, false); } catch (Exception) { } } }
                if (contou)
                {
                    Interlocked.Decrement(ref clientes);
                    Console.WriteLine("  Celular desconectou: " + remoto);
                }
                try { c.Close(); } catch (Exception) { }
            }
        }

        static string ValorQuery(string query, string nome)
        {
            foreach (string par in query.Split('&'))
            {
                int i = par.IndexOf('=');
                if (i > 0 && par.Substring(0, i) == nome) return Uri.UnescapeDataString(par.Substring(i + 1));
            }
            return null;
        }

        // ---------- WebSocket ----------

        static bool LerTudo(Stream s, byte[] buf, int n)
        {
            int lido = 0;
            while (lido < n)
            {
                int r = s.Read(buf, lido, n - lido);
                if (r <= 0) return false;
                lido += r;
            }
            return true;
        }

        static void EnviarQuadro(Stream s, int op, byte[] dados)
        {
            byte[] q = new byte[2 + dados.Length]; // servidor -> navegador nao usa mascara; dados pequenos (< 126)
            q[0] = (byte)(0x80 | op);
            q[1] = (byte)dados.Length;
            Array.Copy(dados, 0, q, 2, dados.Length);
            s.Write(q, 0, q.Length);
        }

        void LacoWebSocket(NetworkStream s, bool[] segurando)
        {
            byte[] cab = new byte[8];
            byte[] mascara = new byte[4];
            while (true)
            {
                if (!LerTudo(s, cab, 2)) return;
                int op = cab[0] & 0x0F;
                bool mascarado = (cab[1] & 0x80) != 0;
                long len = cab[1] & 0x7F;
                if (len == 126)
                {
                    if (!LerTudo(s, cab, 2)) return;
                    len = (cab[0] << 8) | cab[1];
                }
                else if (len == 127)
                {
                    return; // mensagens grandes nao fazem parte do protocolo
                }
                if (len > 1024) return;
                if (mascarado && !LerTudo(s, mascara, 4)) return;
                byte[] dados = new byte[len];
                if (len > 0 && !LerTudo(s, dados, (int)len)) return;
                if (mascarado) { for (int i = 0; i < dados.Length; i++) dados[i] ^= mascara[i & 3]; }

                if (op == 0x8) return;                                  // fechar
                if (op == 0x9) { EnviarQuadro(s, 0xA, dados); continue; } // ping -> pong
                if (op != 0x2 || dados.Length == 0) continue;           // so mensagens binarias

                switch (dados[0])
                {
                    case 1:
                        if (dados.Length >= 5)
                            mouse.Move((short)(dados[1] | (dados[2] << 8)), (short)(dados[3] | (dados[4] << 8)));
                        break;
                    case 2:
                        if (dados.Length >= 3 && dados[1] < 3)
                        {
                            bool baixo = dados[2] != 0;
                            segurando[dados[1]] = baixo;
                            mouse.Button(dados[1], baixo);
                        }
                        break;
                    case 3:
                        if (dados.Length >= 5)
                            mouse.Scroll((short)(dados[1] | (dados[2] << 8)), (short)(dados[3] | (dados[4] << 8)));
                        break;
                    case 5:
                        EnviarQuadro(s, 0x2, dados);
                        break;
                }
            }
        }
    }

    public static class Programa
    {
        static string LerOuCriarToken(string dir)
        {
            string arq = Path.Combine(dir, ".token");
            try
            {
                if (File.Exists(arq))
                {
                    string t = File.ReadAllText(arq).Trim();
                    if (t.Length >= 6) return t;
                }
            }
            catch (Exception) { }

            const string alfabeto = "abcdefghjkmnpqrstuvwxyz23456789";
            byte[] r = new byte[10];
            using (RandomNumberGenerator g = RandomNumberGenerator.Create()) { g.GetBytes(r); }
            StringBuilder sb = new StringBuilder();
            foreach (byte b in r) sb.Append(alfabeto[b % alfabeto.Length]);
            try { File.WriteAllText(arq, sb.ToString()); } catch (Exception) { }
            return sb.ToString();
        }

        public static void Executar(string dir, int porta, bool abrirNavegador)
        {
            bool windows = Environment.OSVersion.Platform == PlatformID.Win32NT;
            IMouse mouse;
            if (windows) mouse = new WindowsMouse(); else mouse = new LogMouse();

            string token = LerOuCriarToken(dir);
            Servidor srv = new Servidor(Path.Combine(dir, "web"), token, mouse, porta);

            // O servidor precisa abrir a porta antes de mostrarmos os enderecos.
            Thread t = new Thread(delegate ()
            {
                try { srv.Rodar(); }
                catch (Exception ex) { Console.WriteLine("Erro: " + ex.Message); Environment.Exit(1); }
            });
            t.IsBackground = true;
            t.Start();
            Thread.Sleep(400);

            Console.WriteLine();
            Console.WriteLine("  ==============================================");
            Console.WriteLine("   CELULAR MOUSE  -  servidor ligado");
            Console.WriteLine("  ==============================================");
            Console.WriteLine();
            Console.WriteLine("  No celular (mesmo Wi-Fi do PC), abra um destes enderecos");
            Console.WriteLine("  ou escaneie o QR code da janela do navegador:");
            Console.WriteLine();
            foreach (Servidor.Endereco e in Servidor.EnderecosLocais())
                Console.WriteLine("    http://" + e.Ip + ":" + srv.Porta + "/?t=" + token + "   (" + e.Nome + ")");
            Console.WriteLine();
            Console.WriteLine("  Para encerrar: feche esta janela ou aperte Ctrl+C.");
            Console.WriteLine();

            if (abrirNavegador && windows)
            {
                try { Process.Start("http://127.0.0.1:" + srv.Porta + "/qr"); } catch (Exception) { }
            }

            t.Join();
        }

        // Para testar fora do PowerShell: mono celular.exe <pasta> [porta]
        public static void Main(string[] args)
        {
            string dir = args.Length > 0 ? args[0] : AppDomain.CurrentDomain.BaseDirectory;
            int porta = args.Length > 1 ? int.Parse(args[1]) : 8765;
            Executar(dir, porta, false);
        }
    }
}
