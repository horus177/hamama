from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # إضافة مكتبة الرسائل
from django.db.models import Sum
from datetime import date
from .models import UserProfile, LoftOrRoom, PigeonPair, ProductionRecord, Sale, Expense
from .forms import PigeonPairForm
from .models import ProductionRecord, Sale, Expense  # عدل أسماء النماذج حسب المشروع لديك


# 0. صفحة الهبوط للزوار غير المسجلين
def landing(request):
    if request.user.is_authenticated:
        return redirect('farm_home')
    return render(request, 'farm/landing.html')


# 0.1 اختيار نوع التربية للمستخدم
@login_required
def select_type_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        farm_type = request.POST.get('farm_type')
        if farm_type in ['cages', 'collective', 'loft']:
            profile.farm_type = 'collective' if farm_type == 'loft' else farm_type
            profile.save()
            messages.success(request, 'تم حفظ نظام التربية بنجاح! 🕊️')
            return redirect('farm_home')
    return render(request, 'farm/select_type.html', {'profile': profile})


# 1. لوحة التحكم الرئيسية
@login_required
def farm_home_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    user_records = ProductionRecord.objects.filter(user=request.user)
    user_sales = Sale.objects.filter(user=request.user)
    user_expenses = Expense.objects.filter(user=request.user)

    total_eggs = user_records.aggregate(total=Sum('eggs_found'))['total'] or 0
    total_squabs = user_records.aggregate(total=Sum('squabs_hatched'))['total'] or 0
    total_deaths = user_records.aggregate(total=Sum('deaths'))['total'] or 0
    
    
    total_sales_amount = user_sales.aggregate(total=Sum('price'))['total'] or 0
    total_expenses_amount = user_expenses.aggregate(total=Sum('amount'))['total'] or 0
    net_profit = total_sales_amount - total_expenses_amount

    # جميع سجلات التحضين الجارية
    upcoming_hatches = user_records.filter(incubation_start_date__isnull=False)

    today = date.today()
    hatches_due_today = []
    active_upcoming_hatches = []

    for rec in upcoming_hatches:
        if hasattr(rec, 'expected_hatch_date') and rec.expected_hatch_date:
            # 1. فلترة التنبيهات: يظهر فقط إذا كان تاريخ الفقس المتوقع هو "اليوم" تماماً
            if rec.expected_hatch_date == today:
                hatches_due_today.append(rec)
            
            # 2. فلترة جدول المواعيد القادمة: عرض المواعيد التي لم تنقضِ بعد (اليوم أو مستقبلاً)
            if rec.expected_hatch_date >= today:
                active_upcoming_hatches.append(rec)

    context = {
        'profile': profile,
        'total_eggs': total_eggs,
        'total_squabs': total_squabs,
        'total_deaths': total_deaths,
        'total_sales': total_sales_amount,
        'total_expenses': total_expenses_amount,
        'net_profit': net_profit,
        'upcoming_hatches': active_upcoming_hatches, # المواعيد الحالية والقادمة فقط
        'hatches_due_today': hatches_due_today,     # المستحقة اليوم فقط
        'pairs': PigeonPair.objects.filter(user=request.user) if profile.farm_type == 'cages' else None,
        'rooms': LoftOrRoom.objects.filter(user=request.user)
    }
    return render(request, 'farm/dashboard.html', context)
# 2. تفاصيل القص
@login_required
def pair_detail_view(request, pair_id):
    pair = get_object_or_404(PigeonPair, id=pair_id, user=request.user)
    records = ProductionRecord.objects.filter(pigeon_pair=pair)
    sales = Sale.objects.filter(pigeon_pair=pair)

    total_eggs = records.aggregate(total=Sum('eggs_found'))['total'] or 0
    total_squabs = records.aggregate(total=Sum('squabs_hatched'))['total'] or 0
    total_deaths = records.aggregate(total=Sum('deaths'))['total'] or 0
    pair_sales_total = sales.aggregate(total=Sum('price'))['total'] or 0
        
# التعديل هنا: الترتيب بحقل record_date
    recent_records = records.order_by('-record_date')[:10]
    context = {
        'pair': pair,
        'total_eggs': total_eggs,
        'total_squabs': total_squabs,
        'total_deaths': total_deaths,
        'pair_sales_total': pair_sales_total,
        'recent_records': recent_records,
    }
    return render(request, 'farm/pair_detail.html', context)


# 3. إدخال سجل إنتاج جديد
@login_required
def add_production_view(request):
    if request.method == 'POST':
        pair_id = request.POST.get('pair')
        room_id = request.POST.get('room')
        eggs_found = int(request.POST.get('eggs_found') or 0)
        squabs_hatched = int(request.POST.get('squabs_hatched') or 0)
        deaths = int(request.POST.get('deaths') or 0)
        incubation_start = request.POST.get('incubation_start_date') or None

        pair = PigeonPair.objects.filter(id=pair_id, user=request.user).first() if pair_id else None
        room = LoftOrRoom.objects.filter(id=room_id, user=request.user).first() if room_id else (pair.loft_or_room if pair else None)

        if room:
            # نتحقق: إذا كان المربي يسجل حصى جديد (eggs_found > 0) نأخذ تاريخ التراقد.
            # أما إذا كان يسجل زغاليل فقط أو نافق، فلن نسجل تاريخ تراقد جديد لهذا السجل.
            final_incubation_date = incubation_start if (eggs_found > 0 and incubation_start) else None

            ProductionRecord.objects.create(
                user=request.user,
                pigeon_pair=pair,
                loft_or_room=room,
                eggs_found=eggs_found,
                squabs_hatched=squabs_hatched,
                deaths=deaths,
                incubation_start_date=final_incubation_date,
            )
            messages.success(request, 'تم تسجيل بيانات الإنتاج بنجاح! 🪺')
        else:
            messages.error(request, 'حدث خطأ: يُرجى اختيار غرفة أو قص صحيح.')
        return redirect('farm_home')
    
    pairs = PigeonPair.objects.filter(user=request.user)
    rooms = LoftOrRoom.objects.filter(user=request.user)
    return render(request, 'farm/add_production.html', {'pairs': pairs, 'rooms': rooms})

# 4. إضافة قص جديد
@login_required
def add_pair_view(request):
    if request.method == 'POST':
        pair_code = request.POST.get('pair_code')
        breed = request.POST.get('breed', '')
        room_id = request.POST.get('room')
        image = request.FILES.get('image')

        room = LoftOrRoom.objects.filter(id=room_id, user=request.user).first() if room_id else None

        if room:
            PigeonPair.objects.create(
                user=request.user,
                loft_or_room=room,
                pair_code=pair_code,
                breed=breed,
                image=image
            )
            messages.success(request, f'تمت إضافة القص {pair_code} بنجاح! 🕊️')
        else:
            messages.error(request, 'يرجى تحديد الغرفة الخاصة بالقص.')
        return redirect('farm_home')
    
    rooms = LoftOrRoom.objects.filter(user=request.user)
    return render(request, 'farm/add_pair.html', {'rooms': rooms})


# 5. إضافة غرفة جديدة
@login_required
def add_room_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            LoftOrRoom.objects.create(
                user=request.user,
                name=name
            )
            messages.success(request, f'تمت إضافة الغرفة ({name}) بنجاح! 🏠')
        return redirect('farm_home')
    
    return render(request, 'farm/add_room.html')


# 6. إضافة مبيعات
@login_required
def add_sale_view(request):
    if request.method == 'POST':
        pair_id = request.POST.get('pair')
        title = request.POST.get('title') or "مبيعات عامة"
        quantity = request.POST.get('quantity') or 1
        price = request.POST.get('price') or 0

        pair = PigeonPair.objects.filter(id=pair_id, user=request.user).first() if pair_id else None

        Sale.objects.create(
            user=request.user,
            pigeon_pair=pair,
            title=title,
            quantity=int(quantity),
            price=float(price)
        )
        messages.success(request, f'تم تسجيل عملية بيع بـ {price} ج.م بنجاح! 💰')
        return redirect('farm_home')
    
    pairs = PigeonPair.objects.filter(user=request.user)
    return render(request, 'farm/add_sale.html', {'pairs': pairs})


# 7. إضافة مصروفات
@login_required
def add_expense_view(request):
    if request.method == 'POST':
        title = request.POST.get('title') or "مصاريف عامة"
        amount = request.POST.get('amount') or 0

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=float(amount)
        )
        messages.success(request, f'تم تسجيل مصروفات بقيمة {amount} ج.م! 📉')
        return redirect('farm_home')
    
    return render(request, 'farm/add_expense.html')

# 8. صفحة سجل وأرشيف التذكيرات والفقس
@login_required
def hatch_history_view(request):
    # جلب كافة السجلات التي تحتوي على تاريخ تحضين للمستخدم الحالي مرتبة من الأحدث للأقدم
    incubation_records = ProductionRecord.objects.filter(
        user=request.user,
        incubation_start_date__isnull=False
    ).order_by('-incubation_start_date')

    today = date.today()

    context = {
        'incubation_records': incubation_records,
        'today': today,
    }
    return render(request, 'farm/hatch_history.html', context) 




# قائمة أقصاص الإنتاج
@login_required
def pairs_list_view(request):
    pairs = PigeonPair.objects.filter(user=request.user)
    return render(request, 'farm/pairs_list.html', {'pairs': pairs})

# تعديل قص (تغيير الصورة، النوع، أو أسباب التبديل)
@login_required
def edit_pair_view(request, pair_id):
    pair = get_object_or_404(PigeonPair, id=pair_id, user=request.user)
    
    if request.method == 'POST':
        form = PigeonPairForm(request.POST, request.FILES, instance=pair)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث بيانات القص ({pair.pair_code}) بنجاح! 🕊️')
            return redirect('pair_detail', pair_id=pair.id)
    else:
        form = PigeonPairForm(instance=pair)

    return render(request, 'farm/edit_pair.html', {'form': form, 'pair': pair})       



# 1. سجل المبيعات الكامل
@login_required
def sales_history(view_request):
    sales = Sale.objects.filter(user=view_request.user).order_by('-sale_date')
    return render(view_request, 'farm/sales_history.html', {'sales': sales})

# 1. عرض سجل النفوق الكامل
@login_required
def deaths_history(view_request):
    # الفلترة بالحقل الصحيح (deaths) والترتيب بتاريخ السجل (record_date)
    deaths = ProductionRecord.objects.filter(
        user=view_request.user, 
        deaths__gt=0
    ).order_by('-record_date')
    
    return render(view_request, 'farm/deaths_history.html', {'deaths': deaths})


# 2. معالجة زر "نافق" للبيض الكابس أو التالف
@login_required
def mark_egg_as_dead(view_request, record_id):
    production = get_object_or_404(ProductionRecord, id=record_id, user=view_request.user)
    
    if view_request.method == 'POST':
        dead_eggs = production.eggs_found
        production.deaths += dead_eggs  # إضافة عدد البيض للنافق
        production.eggs_found = 0       # تصفير البيض حتى يختفي من المتابعة
        production.save()
        
        messages.warning(view_request, f"تم تسجيل عدد ({dead_eggs}) حصى كنافق وحذفه من التنبيهات النشطة.")
    
    return redirect('farm_home')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# سجل المصروفات الكامل مع خيار الطباعة
@login_required
def expenses_history(request):
    # جلب جميع المصروفات للمستخدم مرتبة من الأحدث للأقدم
    expenses = Expense.objects.filter(user=request.user).order_by('-expense_date')
    
    # حساب إجمالي المصروفات
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
    }
    return render(request, 'farm/expenses_history.html', context)    