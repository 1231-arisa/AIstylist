$(document).ready(function() {
    // Add hidden buttons if they don't exist in the DOM
    if ($('#takePhotoBtn').length === 0) {
        $('body').append('<button id="takePhotoBtn" style="display: none;"></button>');
    }
    if ($('#galleryBtn').length === 0) {
        $('body').append('<button id="galleryBtn" style="display: none;"></button>');
    }
    
    var $photoInput = $('#photoInput');
    var $photoPreview = $('#photoPreview');

    // Open camera when Take Photo is clicked
    $('#takePhotoBtn').on('click', async function() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            
            // Create a temporary video element
            const video = document.createElement('video');
            video.srcObject = stream;
            await video.play();

            // Create a canvas to capture the photo
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Take the photo
            canvas.getContext('2d').drawImage(video, 0, 0);
            const imageUrl = canvas.toDataURL('image/jpeg');

            // Update preview with captured image
            $photoPreview.attr('src', imageUrl);
            $photoPreview.show();

            // Stop camera stream
            stream.getTracks().forEach(track => track.stop());

            // Trigger a custom event that can be listened to by other parts of the application
            $(document).trigger('photoTaken', [imageUrl]);
        } catch (error) {
            console.error('Error accessing camera:', error);
            // Fallback to file input if camera access fails
            $photoInput.attr('capture', 'environment');
            $photoInput.click();
        }
    });

    // Open gallery when Choose from Gallery is clicked
    $('#galleryBtn').on('click', function() {
        $photoInput.removeAttr('capture');
        $photoInput.click();
    });

    // Handle photo selection from file input
    $photoInput.on('change', function() {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                $photoPreview.attr('src', e.target.result);
                $photoPreview.show();
                // Trigger a custom event that can be listened to by other parts of the application
                $(document).trigger('photoSelected', [e.target.result]);
            };
            reader.readAsDataURL(file);
        }
    });
});

