from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import OTPCode
from .utils import send_otp_via_email  # دالة إرسال الإيميل المعرفة سابقاً


# --------------------------------------------------
# 1. تسجيل حساب جديد + إرسال OTP
# --------------------------------------------------
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # تفعيل الحساب يتطلب تأكيد OTP أولاً
            user.save()

            # إنشاء كود OTP وإرساله
            otp = OTPCode.generate_otp(user, purpose='VERIFY')
            send_otp_via_email(user, otp.code, purpose="تأكيد الحساب")

            # حفظ معرف المستخدم في الجلسة لمتابعته في صفحة الـ OTP
            request.session['otp_user_id'] = user.id
            messages.success(request, 'تم إنشاء الحساب بنجاح! تم إرسال رمز التحقق إلى بريدك الإلكتروني.')
            return redirect('verify_otp')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


# --------------------------------------------------
# 2. تأكيد رمز التحقق (OTP) للتسجيل
# --------------------------------------------------
def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'جلسة غير صالحة. يرجى محاولة التسجيل مجدداً.')
        return redirect('register')

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, 'المستخدم غير موجود.')
        return redirect('register')

    if request.method == 'POST':
        input_code = request.POST.get('otp_code', '').strip()
        otp = OTPCode.objects.filter(user=user, code=input_code, purpose='VERIFY', is_used=False).last()

        if otp and otp.is_valid():
            otp.is_used = True
            otp.save()

            user.is_active = True  # تفعيل حساب المستخدم
            user.save()

            login(request, user)  # تسجيل الدخول تلقائياً
            del request.session['otp_user_id']  # تنظيف الجلسة
            messages.success(request, 'تم تأكيد حسابك بنجاح! مرحباً بك في مزرعتي.')
            return redirect('select_farm_type')
        else:
            messages.error(request, 'رمز التحقق غير صحيح أو انتهت صلاحيته (صالحة لمدة 5 دقائق).')

    return render(request, 'verify_otp.html')


# --------------------------------------------------
# 3. إعادة إرسال رمز التحقق (Resend OTP)
# --------------------------------------------------
def resend_otp_view(request):
    user_id = request.session.get('otp_user_id') or request.session.get('reset_user_id')
    if user_id:
        user = User.objects.filter(id=user_id).first()
        if user:
            purpose = 'RESET' if request.session.get('reset_user_id') else 'VERIFY'
            title = "إعادة تعيين كلمة السر" if purpose == 'RESET' else "تأكيد الحساب"
            
            otp = OTPCode.generate_otp(user, purpose=purpose)
            send_otp_via_email(user, otp.code, purpose=title)
            messages.info(request, 'تم إعادة إرسال رمز تحقق جديد إلى بريدك الإلكتروني.')
            
            if purpose == 'RESET':
                return redirect('reset_password')
            return redirect('verify_otp')

    messages.error(request, 'تعذر إعادة إرسال الرمز، يرجى إعادة المحاولة.')
    return redirect('login')


# --------------------------------------------------
# 4. نسيت كلمة السر (طلب كود إعادة التعيين)
# --------------------------------------------------
def forgot_password_view(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('identifier', '').strip()
        user = User.objects.filter(email=email_or_username).first() or User.objects.filter(username=email_or_username).first()

        if user:
            otp = OTPCode.generate_otp(user, purpose='RESET')
            send_otp_via_email(user, otp.code, purpose="إعادة تعيين كلمة السر")
            
            request.session['reset_user_id'] = user.id
            messages.success(request, 'تم إرسال رمز استعادة كلمة السر إلى بريدك الإلكتروني.')
            return redirect('reset_password')
        else:
            messages.error(request, 'لم نجد حساباً مرتبطة بهذه البيانات.')

    return render(request, 'forgot_password.html')


# --------------------------------------------------
# 5. أدخال الـ OTP وكلمة السر الجديدة
# --------------------------------------------------
def reset_password_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'جلسة غير صالحة. يرجى طلب استعادة كلمة السر مجدداً.')
        return redirect('forgot_password')

    user = User.objects.filter(id=user_id).first()

    if request.method == 'POST':
        input_code = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if new_password != confirm_password:
            messages.error(request, 'كلمتا السر غير متطابقتين.')
            return render(request, 'reset_password.html')

        if len(new_password) < 8:
            messages.error(request, 'كلمة السر يجب أن تكون 8 أحرف على الأقل.')
            return render(request, 'reset_password.html')

        otp = OTPCode.objects.filter(user=user, code=input_code, purpose='RESET', is_used=False).last()

        if otp and otp.is_valid():
            otp.is_used = True
            otp.save()

            user.set_password(new_password)
            user.save()

            del request.session['reset_user_id']
            messages.success(request, 'تم تغيير كلمة السر بنجاح! يمكنك الآن تسجيل الدخول.')
            return redirect('login')
        else:
            messages.error(request, 'رمز التحقق غير صحيح أو انتهت صلاحيته.')

    return render(request, 'reset_password.html')