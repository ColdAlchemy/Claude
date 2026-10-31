// Gera o certificado HTTPS local (cert.pfx) sem usar a loja de certificados do Windows.
// Compilado separadamente pelo servidor.ps1: precisa do .NET Framework 4.7.2+ (Windows 10 recente).
// Se nao compilar, o servidor continua so com o modo toque.

using System;
using System.IO;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;

namespace CelularMouse
{
    public static class Certificado
    {
        public static void Criar(string dir)
        {
            string pfx = Path.Combine(dir, "cert.pfx");
            using (RSA rsa = RSA.Create()) // chave so na memoria; nada fica no Windows
            {
                if (rsa.KeySize < 2048) rsa.KeySize = 2048;
                CertificateRequest req = new CertificateRequest("CN=Celular Mouse", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
                req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, true));
                OidCollection eku = new OidCollection();
                eku.Add(new Oid("1.3.6.1.5.5.7.3.1")); // autenticacao de servidor
                req.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(eku, false));
                SubjectAlternativeNameBuilder san = new SubjectAlternativeNameBuilder();
                san.AddDnsName("localhost");
                san.AddDnsName("celular-mouse");
                req.CertificateExtensions.Add(san.Build());

                using (X509Certificate2 cert = req.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow.AddYears(3)))
                {
                    File.WriteAllBytes(pfx, cert.Export(X509ContentType.Pfx, "celular-mouse"));
                }
            }
        }
    }
}
