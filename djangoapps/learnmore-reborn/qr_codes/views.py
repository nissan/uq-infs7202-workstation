from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
import json

from .models import QRCode, QRCodeScan, QRCodeBatch
from .services import QRCodeService


def qr_code_home(request):
    """Home page for QR code features."""
    context = {
        'total_codes': QRCode.objects.count(),
        'total_scans': QRCodeScan.objects.count(),
        'active_codes': QRCode.objects.filter(is_active=True).count(),
        'recent_scans': QRCodeScan.objects.order_by('-scanned_at')[:5]
    }
    return render(request, 'qr_codes/home.html', context)


@login_required
def qr_generator(request):
    """QR code generation interface."""
    # Get available content types
    content_types = ContentType.objects.filter(
        app_label__in=['courses', 'users', 'progress']
    ).order_by('app_label', 'model')
    
    # Get existing batches
    batches = QRCodeBatch.objects.filter(
        created_by=request.user
    ).order_by('-created_at')
    
    context = {
        'content_types': content_types,
        'batches': batches
    }
    
    if request.method == 'POST':
        # Handle QR code generation request
        content_type_id = request.POST.get('content_type')
        object_id = request.POST.get('object_id')
        
        if content_type_id and object_id:
            content_type = ContentType.objects.get(id=content_type_id)
            
            # Check if object exists
            try:
                target_object = content_type.get_object_for_this_type(pk=object_id)
                
                # Create or get QR code
                qr_code, created = QRCode.objects.get_or_create(
                    content_type=content_type,
                    object_id=object_id,
                    defaults={
                        'is_active': True,
                        'access_level': request.POST.get('access_level', 'public')
                    }
                )
                
                # Generate QR code image if needed
                if created or not qr_code.image_data:
                    QRCodeService.generate_qr_image(qr_code)
                
                context['qr_code'] = qr_code
                context['target_object'] = target_object
                messages.success(request, 'QR code generated successfully')
                
            except Exception as e:
                messages.error(request, f'Error generating QR code: {str(e)}')
    
    return render(request, 'qr_codes/generator/base.html', context)


@login_required
def qr_scanner(request):
    """QR code scanning interface."""
    context = {}
    return render(request, 'qr_codes/scanner/base.html', context)


@csrf_exempt
def scan_qr_code(request):
    """API endpoint for scanning QR codes."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        qr_code_id = data.get('id')
        
        if not qr_code_id:
            return JsonResponse({'error': 'QR code ID is required'}, status=400)
        
        # Validate scan
        is_valid, message, qr_code = QRCodeService.validate_scan(
            qr_code_id, 
            user=request.user if request.user.is_authenticated else None
        )
        
        if not is_valid:
            return JsonResponse({'error': message}, status=403)
        
        # Record scan
        scan = QRCodeScan.objects.create(
            qr_code=qr_code,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            context_data=data.get('context_data', {}),
            status='success'
        )
        
        # Update scan count
        qr_code.current_scans += 1
        qr_code.save()
        
        # Get target object details
        target_object = qr_code.content_object
        target_name = str(target_object)
        target_url = None
        
        # Determine redirect URL based on content type
        if qr_code.content_type.model == 'course':
            from django.urls import reverse
            target_url = reverse('courses:course-detail', kwargs={'pk': target_object.id})
        elif qr_code.content_type.model == 'module':
            from django.urls import reverse
            target_url = reverse('courses:module-detail', kwargs={'pk': target_object.id})
        
        return JsonResponse({
            'success': True,
            'scan_id': str(scan.id),
            'target_type': qr_code.content_type.model,
            'target_id': qr_code.object_id,
            'target_name': target_name,
            'target_url': target_url,
            'message': 'QR code scanned successfully'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def qr_management(request):
    """QR code management interface."""
    # Get QR codes for current user
    qr_codes = QRCode.objects.all().order_by('-created_at')
    
    # Get batches
    batches = QRCodeBatch.objects.all().order_by('-created_at')
    
    context = {
        'qr_codes': qr_codes,
        'batches': batches
    }
    
    return render(request, 'qr_codes/management/base.html', context)


@login_required
def qr_analytics(request):
    """QR code analytics dashboard."""
    # Get basic statistics
    total_codes = QRCode.objects.count()
    total_scans = QRCodeScan.objects.count()
    active_codes = QRCode.objects.filter(is_active=True).count()
    
    # Get scans per day (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    scans_by_day = QRCodeScan.objects.filter(
        scanned_at__gte=thirty_days_ago
    ).annotate(
        day=TruncDay('scanned_at')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # Get top scanned QR codes
    top_codes = QRCode.objects.annotate(
        scans_count=Count('scans')
    ).order_by('-scans_count')[:10]
    
    context = {
        'total_codes': total_codes,
        'total_scans': total_scans,
        'active_codes': active_codes,
        'scans_by_day': list(scans_by_day),
        'top_codes': top_codes
    }
    
    return render(request, 'qr_codes/analytics/base.html', context)