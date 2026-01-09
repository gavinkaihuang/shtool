import secrets
import binascii

# 在这里修改你想伪装的域名
domain = "cloudflare.com" 

# 生成随机的32字符hex密钥
random_key = secrets.token_hex(16)

# 将域名转换为hex
domain_hex = binascii.hexlify(domain.encode()).decode()

# 拼接：ee + 随机密钥 + 域名hex
final_secret = "ee" + random_key + domain_hex

print(f"您的 Fake TLS Secret 是: {final_secret}")