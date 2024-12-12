#!/bin/bash

# Check if a domain name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

domain="$1"

# Perform nmap ssl-cert script
echo "\n=== Nmap SSL Certificate Scan for $domain ==="
nmap_output=$(nmap --script ssl-cert -p 443 "$domain")
echo "$nmap_output"

# Extract certificate validity from nmap output
valid_from=$(echo "$nmap_output" | grep "Not valid before" | awk -F": " '{print $2}')
valid_to=$(echo "$nmap_output" | grep "Not valid after" | awk -F": " '{print $2}')
issuer=$(echo "$nmap_output" | grep "Issuer" | awk -F": " '{print $2}')
san=$(echo "$nmap_output" | grep "Subject Alternative Name" | awk -F": " '{print $2}')

# Display certificate details
echo "\n=== Extracted Certificate Details ==="
echo "Issuer: $issuer"
echo "Validity: $valid_from to $valid_to"
echo "Subject Alternative Names: $san"

# Use openssl to verify certificate
echo "\n=== OpenSSL Certificate Verification ==="
openssl_output=$(openssl s_client -connect "$domain":443 -servername "$domain" < /dev/null 2>/dev/null)
echo "$openssl_output" | grep "Verify return code"
echo "$openssl_output" | grep "issuer"

echo "\n=== Certificate Fingerprint Validation ==="
# Extract SHA-1 fingerprint using OpenSSL
fingerprint=$(echo "$openssl_output" | openssl x509 -noout -fingerprint -sha1)
echo "SHA-1 Fingerprint: $fingerprint"

# Check if the domain matches SAN or CN
echo "\n=== Domain Validation ==="
if [[ "$san" == *"$domain"* ]]; then
    echo "The domain $domain is valid for this certificate."
else
    echo "The domain $domain is NOT valid for this certificate!"
fi

# Output summary
echo "\n=== Summary ==="
echo "Certificate issued by: $issuer"
echo "Valid from: $valid_from"
echo "Valid to: $valid_to"
echo "Subject Alternative Names: $san"
