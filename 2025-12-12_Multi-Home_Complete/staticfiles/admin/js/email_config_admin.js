/**
 * Email Configuration Admin JavaScript
 * Auto-fills host/port settings when provider is selected
 */

(function($) {
    'use strict';
    
    $(document).ready(function() {
        var providerField = $('#id_provider');
        var hostField = $('#id_host');
        var portField = $('#id_port');
        var tlsField = $('#id_use_tls');
        var sslField = $('#id_use_ssl');
        
        // Provider defaults
        var providerDefaults = {
            'gmail': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'use_tls': true,
                'use_ssl': false,
                'help': 'Gmail requires an App Password. Enable 2FA on your Google account, then generate an app password at: https://myaccount.google.com/apppasswords'
            },
            'sendgrid': {
                'host': 'smtp.sendgrid.net',
                'port': 587,
                'use_tls': true,
                'use_ssl': false,
                'help': 'SendGrid username is always "apikey". Password is your SendGrid API key. Free tier: 100 emails/day.'
            },
            'microsoft365': {
                'host': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': true,
                'use_ssl': false,
                'help': 'Microsoft 365 / Outlook.com requires an App Password if 2FA is enabled. Generate at: https://account.live.com/proofs/AppPassword'
            },
            'custom': {
                'host': '',
                'port': 587,
                'use_tls': true,
                'use_ssl': false,
                'help': 'Enter your custom SMTP server details. Contact your email provider for connection settings.'
            }
        };
        
        // Update fields when provider changes
        providerField.change(function() {
            var selectedProvider = $(this).val();
            var defaults = providerDefaults[selectedProvider];
            
            if (defaults) {
                // Auto-fill fields
                hostField.val(defaults.host);
                portField.val(defaults.port);
                tlsField.prop('checked', defaults.use_tls);
                sslField.prop('checked', defaults.use_ssl);
                
                // Show helpful message
                showProviderHelp(selectedProvider, defaults.help);
            }
        });
        
        // Show help message
        function showProviderHelp(provider, helpText) {
            // Remove existing help
            $('.email-provider-help').remove();
            
            // Create help box
            var helpBox = $('<div class="email-provider-help" style="background: #e8f4f8; border-left: 4px solid #2196F3; padding: 12px; margin: 10px 0; border-radius: 4px;">' +
                '<strong>📧 ' + provider.toUpperCase() + ' Setup:</strong><br>' +
                helpText +
                '</div>');
            
            // Insert after provider field
            providerField.closest('.form-row').after(helpBox);
        }
        
        // Validate TLS/SSL combination
        tlsField.change(validateTlsSsl);
        sslField.change(validateTlsSsl);
        
        function validateTlsSsl() {
            var bothEnabled = tlsField.is(':checked') && sslField.is(':checked');
            
            // Remove existing warning
            $('.tls-ssl-warning').remove();
            
            if (bothEnabled) {
                var warning = $('<div class="tls-ssl-warning" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 10px 0; border-radius: 4px;">' +
                    '<strong>⚠ Warning:</strong> Both TLS and SSL are enabled. This is usually incorrect. ' +
                    'Use <strong>TLS for port 587</strong> or <strong>SSL for port 465</strong>, not both.' +
                    '</div>');
                
                sslField.closest('.form-row').after(warning);
            }
        }
        
        // Port validation
        portField.change(function() {
            var port = parseInt($(this).val());
            var isTls = tlsField.is(':checked');
            var isSsl = sslField.is(':checked');
            
            // Remove existing warning
            $('.port-warning').remove();
            
            var warning = null;
            
            if (port === 587 && isSsl && !isTls) {
                warning = 'Port 587 is typically used with TLS, not SSL. Consider enabling TLS.';
            } else if (port === 465 && isTls && !isSsl) {
                warning = 'Port 465 is typically used with SSL, not TLS. Consider enabling SSL.';
            } else if (port === 25) {
                warning = 'Port 25 is typically unencrypted and may be blocked by firewalls. Consider using port 587 with TLS.';
            }
            
            if (warning) {
                var warningBox = $('<div class="port-warning" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 10px 0; border-radius: 4px;">' +
                    '<strong>ℹ Note:</strong> ' + warning +
                    '</div>');
                
                portField.closest('.form-row').after(warningBox);
            }
        });
        
        // Trigger initial validation if editing existing config
        if (providerField.val()) {
            providerField.trigger('change');
        }
    });
})(django.jQuery);
