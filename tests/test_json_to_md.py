import pytest
from pipeline import ChatbotUtils

def test_json_to_md():
    # Given JSON input
    json_data = {
        "APISecurityPolicy": {
            "Purpose": "To establish a comprehensive framework for securing Application Programming Interfaces (APIs) to protect organizational data and services from unauthorized access and vulnerabilities.",
            "Scope": "This policy applies to all APIs developed, deployed, and maintained by the organization, as well as third-party APIs integrated into organizational systems.",
            "PolicyStatement": {
                "APIDesign": {
                    "SecurityByDesign": "APIs must be designed with security considerations from the outset, incorporating security best practices and threat modeling during the development phase.",
                    "DataClassification": "APIs must classify data based on sensitivity and apply appropriate security controls to protect sensitive information."
                },
                "Authentication and Authorization": {
                    "StrongAuthentication": "APIs must implement strong authentication mechanisms, such as OAuth 2.0 or OpenID Connect, to verify the identity of users and applications accessing the API.",
                    "AccessControl": "Role-based access control (RBAC) must be enforced to ensure that users have access only to the resources necessary for their roles."
                },
                "DataProtection": {
                    "Encryption": "All data transmitted through APIs must be encrypted using secure protocols (e.g., TLS 1.2 or higher) to protect against interception and unauthorized access.",
                    "InputValidation": "APIs must validate all input data to prevent injection attacks and ensure that only expected data formats are accepted."
                },
                "Monitoring and Logging": {
                    "ActivityLogging": "All API access and usage must be logged to provide an audit trail for security monitoring and incident response.",
                    "AnomalyDetection": "Automated monitoring tools must be employed to detect unusual patterns of API usage that may indicate security incidents."
                },
                "Vulnerability Management": {
                    "RegularTesting": "APIs must undergo regular security testing, including vulnerability assessments and penetration testing, to identify and remediate security weaknesses.",
                    "PatchManagement": "Timely application of security patches and updates must be enforced to protect against known vulnerabilities."
                },
                "Incident Response": {
                    "IncidentReporting": "All security incidents involving APIs must be reported immediately to the Incident Response Team (IRT) for investigation and remediation.",
                    "PostIncidentReview": "A post-incident review must be conducted to analyze the response to API security incidents and identify areas for improvement."
                },
                "Training and Awareness": {
                    "DeveloperTraining": "All personnel involved in API development and management must receive training on API security best practices and emerging threats.",
                    "OngoingAwareness": "Regular awareness programs should be conducted to keep employees informed about API security risks and mitigation strategies."
                }
            },
            "Compliance": {
                "Standards": "This policy aligns with ISO/IEC 27001, NIST SP 800-53, OWASP API Security Top 10, and other relevant regulatory frameworks."
            }
        }
    }

    # Expected markdown output
    expected_md_output = """# API Security Policy

## Purpose

To establish a comprehensive framework for securing Application Programming Interfaces (APIs) to protect organizational data and services from unauthorized access and vulnerabilities.

## Scope

This policy applies to all APIs developed, deployed, and maintained by the organization, as well as third-party APIs integrated into organizational systems.

## Policy Statement

### API Design

#### Security By Design

APIs must be designed with security considerations from the outset, incorporating security best practices and threat modeling during the development phase.

#### Data Classification

APIs must classify data based on sensitivity and apply appropriate security controls to protect sensitive information.

### Authentication and Authorization

#### Strong Authentication

APIs must implement strong authentication mechanisms, such as OAuth 2.0 or OpenID Connect, to verify the identity of users and applications accessing the API.

#### Access Control

Role-based access control (RBAC) must be enforced to ensure that users have access only to the resources necessary for their roles.

### Data Protection

#### Encryption

All data transmitted through APIs must be encrypted using secure protocols (e.g., TLS 1.2 or higher) to protect against interception and unauthorized access.

#### Input Validation

APIs must validate all input data to prevent injection attacks and ensure that only expected data formats are accepted.

### Monitoring and Logging

#### Activity Logging

All API access and usage must be logged to provide an audit trail for security monitoring and incident response.

#### Anomaly Detection

Automated monitoring tools must be employed to detect unusual patterns of API usage that may indicate security incidents.

### Vulnerability Management

#### Regular Testing

APIs must undergo regular security testing, including vulnerability assessments and penetration testing, to identify and remediate security weaknesses.

#### Patch Management

Timely application of security patches and updates must be enforced to protect against known vulnerabilities.

### Incident Response

#### Incident Reporting

All security incidents involving APIs must be reported immediately to the Incident Response Team (IRT) for investigation and remediation.

#### Post Incident Review

A post-incident review must be conducted to analyze the response to API security incidents and identify areas for improvement.

### Training and Awareness

#### Developer Training

All personnel involved in API development and management must receive training on API security best practices and emerging threats.

#### Ongoing Awareness

Regular awareness programs should be conducted to keep employees informed about API security risks and mitigation strategies.

## Compliance

### Standards

This policy aligns with ISO/IEC 27001, NIST SP 800-53, OWASP API Security Top 10, and other relevant regulatory frameworks.
"""

    # Act: Call the json_to_md function
    actual_md_output = ChatbotUtils.json_to_md(json_data)

    # Assert: Compare the actual and expected markdown outputs
    assert actual_md_output.strip() == expected_md_output.strip(), "Markdown output did not match expected output"
