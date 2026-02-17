"""
Test script for payslip email functionality
Run this from Django shell: python manage.py shell < test_payslip_email.py
"""

from employees.models import Employee
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def test_payslip_email():
    """Test sending a payslip email"""
    
    print("=" * 60)
    print("PAYSLIP EMAIL TEST")
    print("=" * 60)
    
    # Get a test employee (first confirmed employee)
    try:
        employee = Employee.objects.filter(
            period_type='confirmed',
            employment_status='active'
        ).first()
        
        if not employee:
            print("❌ No confirmed employees found for testing")
            print("   Please create a confirmed employee first")
            return
        
        print(f"✓ Found test employee: {employee.full_name}")
        print(f"  Employee ID: {employee.employee_code}")
        print(f"  Email: {employee.official_email}")
        print()
        
        # Email context
        email_context = {
            'employee_name': employee.full_name,
            'employee_code': employee.employee_code,
            'department': employee.department.name,
            'designation': employee.designation.name,
            'month_name': 'January',
            'year': 2026,
        }
        
        print("📧 Rendering email templates...")
        
        # Render templates
        try:
            html_body = render_to_string('emails/payslip_email.html', email_context)
            plain_body = render_to_string('emails/payslip_email.txt', email_context)
            print("✓ HTML template rendered successfully")
            print("✓ Plain text template rendered successfully")
        except Exception as e:
            print(f"❌ Template rendering failed: {str(e)}")
            return
        
        print()
        print("📨 Preparing email...")
        
        # Create email
        subject = f"Payslip for January 2026 - {employee.full_name}"
        
        email = EmailMultiAlternatives(
            subject,
            plain_body,
            settings.DEFAULT_FROM_EMAIL,
            [employee.official_email]
        )
        email.attach_alternative(html_body, "text/html")
        
        # Note: Not attaching actual PDF in test
        print(f"✓ Email prepared")
        print(f"  Subject: {subject}")
        print(f"  From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"  To: {employee.official_email}")
        print()
        
        # Send email
        print("📤 Sending email...")
        try:
            email.send()
            print("✅ Email sent successfully!")
            print()
            print("📬 Check your Mailtrap inbox:")
            print("   URL: https://mailtrap.io")
            print(f"   Host: {settings.EMAIL_HOST}")
            print(f"   User: {settings.EMAIL_HOST_USER}")
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            print()
            print("Troubleshooting:")
            print("1. Check SMTP settings in settings.py")
            print("2. Verify network connectivity")
            print("3. Check email credentials")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_payslip_email()
