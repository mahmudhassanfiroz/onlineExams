(function($) {
    $(document).ready(function() {
        var $adTypeField = $('#id_ad_type');
        var $customAdFields = $('.custom-ad');
        var $googleAdFields = $('.google-ad');

        function toggleAdFields() {
            var adType = $adTypeField.val();
            if (adType === 'custom') {
                $customAdFields.show();
                $googleAdFields.hide();
            } else if (adType === 'google') {
                $customAdFields.hide();
                $googleAdFields.show();
            }
        }

        $adTypeField.change(toggleAdFields);
        toggleAdFields();  // Initial call to set correct state
    });
})(django.jQuery);
