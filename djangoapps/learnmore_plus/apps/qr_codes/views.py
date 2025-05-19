from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import QRCode, QRCodeScan
from .services import QRCodeService
from django.db import models
from apps.courses.models import Course, Module
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint

def scan_qr_code_redirect(request, qr_code_id):
    """Handle QR code scanning and redirect to the appropriate URL."""
    qr_code = get_object_or_404(QRCode, id=qr_code_id)
    
    # Record the scan
    QRCodeService.record_scan(qr_code, request)
    
    # Redirect to the URL
    return redirect(qr_code.url)

@login_required
def scan_qr_code(request):
    """View for scanning QR codes."""
    return render(request, 'qr_codes/scan.html')

class QRCodeDetailView(DetailView):
    """View for displaying QR code details and statistics."""
    model = QRCode
    template_name = 'qr_codes/qr_code_detail.html'
    context_object_name = 'qr_code'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scan_stats'] = QRCodeService.get_scan_stats(self.object)
        qr_code = self.get_object()
        context['scans'] = QRCodeScan.objects.filter(qr_code=qr_code).order_by('-scanned_at')
        return context

@login_required
def qr_code_statistics(request):
    """View for displaying QR code statistics."""
    # Get date range for statistics (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get scan data for the period
    scans = QRCodeScan.objects.filter(
        scanned_at__range=(start_date, end_date)
    ).order_by('scanned_at')
    
    # Prepare data for the chart
    dates = []
    scan_counts = []
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        count = scans.filter(
            scanned_at__range=(current_date, next_date)
        ).count()
        dates.append(current_date.strftime('%Y-%m-%d'))
        scan_counts.append(count)
        current_date = next_date
    
    # Get top QR codes
    top_qr_codes = QRCode.objects.annotate(
        total_scans=models.Count('scans')  # Changed from scan_count to total_scans to avoid conflict
    ).order_by('-total_scans')[:5]
    
    context = {
        'total_scans': QRCodeScan.objects.count(),
        'active_qr_codes': QRCode.objects.count(),
        'average_scans': QRCodeScan.objects.count() / max(QRCode.objects.count(), 1),
        'dates': dates,
        'scan_counts': scan_counts,
        'top_qr_codes': top_qr_codes,
    }
    
    return render(request, 'qr_codes/statistics.html', context)

@login_required
def print_course_qr_codes(request, course_id):
    """Generate a printable sheet with QR codes for a course and its modules."""
    course = get_object_or_404(Course, id=course_id)
    
    # Get course QR code
    course_url = request.build_absolute_uri(
        reverse('courses:course_detail', kwargs={'slug': course.slug})
    )
    course_qr_code = QRCodeService.get_or_create_qr_code(course, course_url)
    
    # Get module QR codes
    modules = course.modules.all().order_by('order')
    module_qr_codes = {}
    for module in modules:
        module_url = request.build_absolute_uri(
            reverse('courses:course_learn', kwargs={'slug': course.slug, 'module_order': module.order})
        )
        module_qr_codes[module.id] = QRCodeService.get_or_create_qr_code(module, module_url)
    
    # Render the template
    context = {
        'course': course,
        'course_qr_code': course_qr_code,
        'modules': modules,
        'module_qr_codes': module_qr_codes,
        'generated_at': timezone.now(),
    }
    
    # Generate PDF
    html_string = render_to_string('qr_codes/print_course_qr_codes.html', context)
    pdf_file = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    
    # Create response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="QR_Codes_{course.slug}.pdf"'
    return response
