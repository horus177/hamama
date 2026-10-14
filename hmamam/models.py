from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date

# 1. ملف بروفايل المستخدم لنوع التربية (سلاكات / سايب)
class UserProfile(models.Model):
    FARM_TYPES = [
        ('cages', 'سلاكات وعيون منفصلة'),
        ('collective', 'تربية جماعية (حمام سايب)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    farm_type = models.CharField(max_length=20, choices=FARM_TYPES, default='cages')

    def __str__(self):
        return f"{self.user.username} - {self.get_farm_type_display()}"

# 2. جدول الغرف / العنابر
class LoftOrRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="صاحب المزرعة")
    name = models.CharField(max_length=50, verbose_name="اسم الغرفة/السلاكة")

    def __str__(self):
        return self.name


# 3. جدول القصاص (خاص بنظام السلاكات)
class PigeonPair(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="صاحب المزرعة")
    loft_or_room = models.ForeignKey(LoftOrRoom, on_delete=models.CASCADE, verbose_name="مكان السكن")
    pair_code = models.CharField(max_length=50, verbose_name="الرقم التعريفي (رقم العين/الدبلة)")
    breed = models.CharField(max_length=50, verbose_name="السلالة/النوع")
    image = models.ImageField(upload_to='pigeons/', blank=True, null=True, verbose_name="صورة القص")
    created_at = models.DateField(auto_now_add=True,null=True, verbose_name="تاريخ التركيب")

    # أضف هذه الحقول الجديدة:
    male_details = models.CharField(max_length=255, blank=True, null=True, verbose_name="تفاصيل الذكر")
    female_details = models.CharField(max_length=255, blank=True, null=True, verbose_name="تفاصيل الأنثى")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"قص {self.pair_code} ({self.breed})"


# 4. جدول سجلات الإنتاج ومواعيد الفقس
class ProductionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    loft_or_room = models.ForeignKey(LoftOrRoom, on_delete=models.CASCADE)
    pigeon_pair = models.ForeignKey(PigeonPair, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="القص")
    
    record_date = models.DateField(auto_now_add=True,null=True, verbose_name="تاريخ السجل")
    eggs_found = models.IntegerField(default=0, verbose_name="عدد الحصى")
    incubation_start_date = models.DateField(blank=True, null=True, verbose_name="تاريخ بدء التحيض/البيض")
    squabs_hatched = models.IntegerField(default=0, verbose_name="عدد الزغاليل الفاقسة")
    deaths = models.IntegerField(default=0, verbose_name="عدد النفوق")

    # خاصية حساب تاريخ الفقس المتوقع (فترة تحضين الحمام 18 يوم)
    @property
    def expected_hatch_date(self):
        if self.incubation_start_date:
            return self.incubation_start_date + timedelta(days=18)
        return None

    # خاصية حساب الأيام المتبقية للفقس
    @property
    def days_until_hatch(self):
        if self.expected_hatch_date:
            remaining = (self.expected_hatch_date - date.today()).days
            return remaining if remaining >= 0 else 0
        return None

    def __str__(self):
        return f"سجل {self.record_date} - {self.loft_or_room.name}"


# 5. جدول المبيعات (مرتبط بالقص ومبلغ البيع)
class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    pigeon_pair = models.ForeignKey(PigeonPair, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="القص المباع منه")
    title = models.CharField(max_length=100,default="مبيعات عامة", verbose_name="بيان البيع (مثلاً: بيع زغاليل)")
    quantity = models.IntegerField(default=1, verbose_name="العدد المباع")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر البيع الإجمالي")
    sale_date = models.DateField(auto_now_add=True,null=True, verbose_name="تاريخ البيع")


# 6. جدول المصاريف (كلفة، أدوية، كهرباء)
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    title = models.CharField(max_length=100,default="مصاريف عامة", verbose_name="بند المصروف (علف، علاج...)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ")
    expense_date = models.DateField(auto_now_add=True,null=True, verbose_name="تاريخ المصروف")