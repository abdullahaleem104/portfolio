// static/admin/js/password_toggle.js
(function($) {
    $(document).ready(function() {
        // Find all password inputs
        $('input[type="password"]').each(function() {
            // Create wrapper
            $(this).wrap('<div class="password-wrapper" style="position: relative; display: inline-block; width: 100%;"></div>');
            
            // Add eye icon
            $(this).after('<span class="toggle-password" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer; z-index: 10; background: white; padding: 0 5px;"><i class="fas fa-eye"></i></span>');
            
            // Add class to input
            $(this).addClass('password-field').css('padding-right', '35px');
            
            // Toggle functionality
            $(this).next('.toggle-password').click(function() {
                var input = $(this).prev('.password-field');
                var type = input.attr('type') === 'password' ? 'text' : 'password';
                input.attr('type', type);
                
                // Toggle icon
                var icon = $(this).find('i');
                if (type === 'text') {
                    icon.removeClass('fa-eye').addClass('fa-eye-slash');
                } else {
                    icon.removeClass('fa-eye-slash').addClass('fa-eye');
                }
            });
        });
    });
})(django.jQuery);