# Security Guide

## Overview
This document outlines the security measures implemented in the Multi-Cloud Operations Dashboard and provides guidance for secure deployment and operation.

## Security Features Implemented

### 1. Authentication & Authorization
- **Azure AD Integration**: Production authentication via Azure Active Directory
- **JWT Token Validation**: Secure token verification with JWKS
- **Role-Based Access Control**: User and admin roles with appropriate permissions
- **Development Mode**: Limited mock authentication for development only

### 2. Input Validation & Sanitization
- **Pydantic Validation**: All API inputs validated using Pydantic schemas
- **SQL Injection Prevention**: Enhanced query validation and parameterization
- **XSS Protection**: Input sanitization and output encoding
- **Request Size Limits**: Maximum request body size enforcement

### 3. API Security
- **Rate Limiting**: 100 requests per minute per IP address
- **CORS Configuration**: Restricted origins, methods, and headers
- **Security Headers**: Comprehensive security headers on all responses
- **Error Handling**: Generic error messages to prevent information leakage

### 4. Database Security
- **Connection Encryption**: SSL/TLS enforcement for database connections
- **Credential Management**: Environment-based credential configuration
- **Query Restrictions**: Only SELECT queries allowed in chat service
- **Connection Pooling**: Proper connection pool configuration

### 5. Container Security
- **Non-Root User**: All containers run as non-privileged users
- **Health Checks**: Container health monitoring
- **Read-Only Filesystem**: Where applicable
- **Minimal Base Images**: Using slim Python and official PostgreSQL images

## Environment Configuration

### Required Environment Variables

```bash
# Security (REQUIRED)
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters-long
ENVIRONMENT=production

# Database (REQUIRED)
DATABASE_URL=postgresql://username:password@host:port/database
DB_USER=appuser
DB_PASSWORD=your-secure-database-password
DB_NAME=dashboard_db

# CORS (REQUIRED for production)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Azure Authentication (REQUIRED for production)
AZURE_CLIENT_ID=your-azure-client-id
AZURE_TENANT_ID=your-azure-tenant-id

# Azure OpenAI (OPTIONAL)
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-openai-api-key
```

### Security Checklist for Production

#### Before Deployment
- [ ] Set strong, unique SECRET_KEY (minimum 32 characters)
- [ ] Configure ENVIRONMENT=production
- [ ] Set secure database credentials
- [ ] Configure proper CORS_ORIGINS for your domain
- [ ] Set up Azure AD authentication
- [ ] Review and update trusted hosts in main.py
- [ ] Enable HTTPS/TLS for all connections
- [ ] Configure proper firewall rules

#### Database Security
- [ ] Use strong database passwords (minimum 16 characters)
- [ ] Enable SSL/TLS for database connections
- [ ] Restrict database access to application servers only
- [ ] Regular database backups with encryption
- [ ] Monitor database access logs

#### Container Security
- [ ] Remove development volume mounts from docker-compose.yml
- [ ] Use specific image tags, not 'latest'
- [ ] Scan container images for vulnerabilities
- [ ] Configure container resource limits
- [ ] Use Docker secrets for sensitive data

#### Network Security
- [ ] Use HTTPS only (no HTTP)
- [ ] Configure proper SSL/TLS certificates
- [ ] Set up Web Application Firewall (WAF)
- [ ] Implement network segmentation
- [ ] Monitor network traffic

#### Monitoring & Logging
- [ ] Set up centralized logging
- [ ] Monitor authentication failures
- [ ] Track API usage and rate limiting
- [ ] Set up security alerts
- [ ] Regular security audits

## Security Best Practices

### 1. Credential Management
- Never commit secrets to version control
- Use environment variables or secure secret management
- Rotate credentials regularly
- Use principle of least privilege

### 2. API Security
- Always validate input data
- Use HTTPS for all communications
- Implement proper error handling
- Monitor for suspicious activity

### 3. Database Security
- Use parameterized queries
- Encrypt sensitive data at rest
- Regular security updates
- Monitor database access

### 4. Container Security
- Keep base images updated
- Use minimal images
- Run as non-root user
- Regular vulnerability scans

## Incident Response

### Security Incident Checklist
1. **Immediate Response**
   - Isolate affected systems
   - Preserve evidence
   - Assess scope of incident

2. **Investigation**
   - Review logs and monitoring data
   - Identify attack vectors
   - Determine data exposure

3. **Containment**
   - Patch vulnerabilities
   - Update credentials
   - Implement additional controls

4. **Recovery**
   - Restore from clean backups
   - Verify system integrity
   - Monitor for continued threats

5. **Post-Incident**
   - Document lessons learned
   - Update security procedures
   - Conduct security review

## Security Updates

### Regular Maintenance
- Update dependencies monthly
- Security patches within 48 hours
- Regular penetration testing
- Code security reviews

### Dependency Management
```bash
# Backend security audit
pip audit

# Frontend security audit
npm audit

# Update dependencies
pip install --upgrade -r requirements.txt
npm update
```

## Contact Information

For security issues or questions:
- Create a security issue in the repository
- Follow responsible disclosure practices
- Include detailed reproduction steps

## Compliance

This application implements security controls aligned with:
- OWASP Top 10
- NIST Cybersecurity Framework
- Azure Security Baseline
- Industry best practices

## Additional Resources

- [OWASP Security Guidelines](https://owasp.org/)
- [Azure Security Documentation](https://docs.microsoft.com/en-us/azure/security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security](https://docs.docker.com/engine/security/)