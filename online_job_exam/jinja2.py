from django_jinja import library
from jinja2 import Environment
from django.utils.html import mark_safe
from django.template.defaultfilters import truncatewords

@library.global_function
def render_packages(title, packages, bg_color, btn_color):
    package_html = f'<div class="py-5 {bg_color}">'
    package_html += f'<div class="container"><h2 class="text-center mb-5">{title}</h2><div class="row">'

    for package in packages:
        package_html += f'''
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    <div class="card-header {btn_color} text-white">
                        <h3 class="card-title text-center">{package.name}</h3>
                    </div>
                    <div class="card-body">
                        <p class="card-text">{mark_safe(truncatewords(package.description, 30))}</p>
                        <h4 class="card-title text-center mb-4">{package.price} টাকা</h4>
                        <p class="card-text">মেয়াদ: {package.duration}</p>
                    </div>
                    <div class="card-footer text-center">
                        <a href="/services/package_detail/{package.slug}/" class="btn {btn_color}">বিস্তারিত দেখুন</a>
                    </div>
                </div>
            </div>
        '''

    package_html += '''
        </div>
    </div>
</div>
    '''

    return package_html

def environment(**options):
    env = Environment(**options)
    return env  # Filters and functions are automatically registered with the library now
