function loadAds() {
    document.querySelectorAll('.ad-placeholder').forEach(placeholder => {
        try {
            const adData = JSON.parse(placeholder.dataset.ad);
            console.log('Ad Data:', adData); // ডিবাগিংয়ের জন্য

            let adContent = '';

            if (adData.type === 'google') {
                console.log('Loading Google Ad');
                const script = document.createElement('script');
                script.innerHTML = adData.content;
                placeholder.appendChild(script);
            } else {
                console.log('Loading Custom Ad');
                if (adData.image_url) {
                    adContent = `<a href="${adData.url || '#'}" target="_blank"><img src="${adData.image_url}" alt="${adData.title || 'Advertisement'}" class="img-fluid"></a>`;
                } else if (adData.url) {
                    adContent = `<a href="${adData.url}" target="_blank">${adData.title || 'Advertisement'}</a>`;
                } else {
                    adContent = adData.content || 'No content available';
                }
                placeholder.innerHTML = adContent;
            }

            // Remove loader and show ad
            const loader = placeholder.querySelector('.ad-loader');
            if (loader) {
                loader.remove();
            }
            
            placeholder.style.opacity = '0';
            setTimeout(() => {
                placeholder.style.transition = 'opacity 0.5s';
                placeholder.style.opacity = '1';
            }, Math.random() * 1000); // Random delay for more realistic loading

        } catch (error) {
            console.error('Error loading ad:', error);
            placeholder.innerHTML = 'Error loading advertisement';
        }
    });
}

// DOMContentLoaded ইভেন্ট ব্যবহার করুন
document.addEventListener('DOMContentLoaded', loadAds);
