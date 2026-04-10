# 🕌 IlmQuiz (Islamic Knowledge Challenge )- تحدي المعرفة الإسلامية

![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Framework](https://img.shields.io/badge/PySide6-Qt-green.svg)
![Platform](https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Accessibility](https://img.shields.io/badge/Accessibility-100%25-success.svg)

**IlmQuiz** هي لعبة مسابقات ثقافية إسلامية تفاعلية ومفتوحة المصدر، تهدف إلى إثراء المعرفة الدينية بطريقة ممتعة وشيقة. تم تصميم اللعبة لتعمل على جميع أنظمة التشغيل بكفاءة عالية، مع التركيز الاستثنائي على إمكانية الوصول (Accessibility) لضمان تجربة لعب شاملة للجميع، بما في ذلك المكفوفين وضعاف البصر.

---

## ✨ المميزات الرئيسية (Key Features)

* 🎯 **تجربة لعب متدرجة:** تحتوي اللعبة على تصنيفات متعددة (تفسير، عقيدة، فقه، سيرة، حديث، لغة عربية) مع 3 مستويات صعوبة (سهل، متوسط، صعب) تفتح تدريجياً.
* ♿ **إمكانية الوصول الكاملة (100% Accessible):** دعم برمجي عميق لقارئات الشاشة عبر محرك `TTS` مخصص:
  * **Windows:** مدعوم عبر `UniversalSpeech` (NVDA, JAWS, SAPI).
  * **macOS:** دعم مباشر لـ `VoiceOver` عبر `appscript` و `osascript`.
  * **Linux:** دعم لـ `Orca` و `Speech-Dispatcher`.
* 🔄 **نظام تحديث تلقائي (Smart Auto-Updater):** نظام مدمج يفحص التحديثات في الخلفية ويقوم بتنزيلها وتثبيتها بصمت (Silently) دون تدخل المستخدم، مع دعم النسخ المثبتة والمحمولة.
* 🎨 **واجهة مستخدم مرنة وجميلة:** * تصميم يعتمد على `QStackedWidget` لانتقالات سريعة.
  * تأثيرات بصرية حركية (Fade, Shake, Glow).
  * الوضع الليلي (Dark Theme) ووضع التباين العالي (High Contrast).
  * إمكانية تكبير خط الأسئلة برمجياً (Dynamic Font Scaling).
* ⚙️ **معمارية قوية (MVVM):** كود نظيف ومفصول إلى طبقات (Core, Data, Services, UI) لتسهيل الصيانة والتطوير.

---

## 📥 التحميل والتثبيت (Downloads)

اللعبة متاحة للتحميل مجاناً لجميع أنظمة التشغيل (نسخ تثبيت ونسخ محمولة).
يمكنك تحميل أحدث إصدار من صفحة **[الإصدارات (Releases)](https://github.com/MesterPerfect/IlmQuiz/releases)**.

* **Windows:** `IlmQuiz_Setup_vX.X.X.exe` (تثبيت) أو `IlmQuiz_Windows_Portable.zip` (محمولة)
* **macOS:** `IlmQuiz_macOS_Installer.dmg` (تثبيت) أو `IlmQuiz_macOS_Portable.zip` (محمولة)
* **Linux:** `IlmQuiz_Linux_Installer.deb` (تثبيت) أو `IlmQuiz_Linux_Portable.tar.gz` (محمولة)

---

## 🛠️ للمطورين (For Developers)

تم بناء المشروع باستخدام لغة **Python** وإطار عمل **PySide6**.

### إعداد بيئة التطوير (Setup Environment)
1. قم باستنساخ المستودع:
   ```bash
   git clone https://github.com/MesterPerfect/IlmQuiz.git
   cd IlmQuiz
   ```
2. قم بإنشاء بيئة افتراضية وتفعيلها:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS / Linux:
   source venv/bin/activate
   ```
3. ثبّت الحزم المطلوبة:
   ```bash
   pip install -r requirements.txt
   ```
4. قم بتشغيل اللعبة:
   ```bash
   python main.py
   ```

### 🏗️ الهيكل المعماري للمشروع (Architecture)
يعتمد المشروع على معمارية الطبقات لضمان نظافة الكود (Clean Code):
* `core/`: يحتوي على محرك اللعبة الأساسي (`GameEngine`) وإدارة الحالة وإعدادات المسارات الثابتة.
* `data/`: يتعامل مع قاعدة بيانات `SQLite` ويحتوي على النماذج (`Models`) ونظام الـ Queries السريع.
* `services/`: يحتوي على الخدمات المنفصلة (نظام التحديثات، نظام تحويل النص لكلام `TTS`، الصوتيات، وإدارة الإعدادات).
* `ui/`: يحتوي على نوافذ الواجهة (`Windows`)، المكونات المشتركة، والتأثيرات البصرية، ونموذج العرض (`GameViewModel`).
* `apply_update.py`: سكربت خارجي مستقل لإدارة الكتابة فوق الملفات أثناء التحديث التلقائي.

---

## ⚙️ البناء والنشر الأوتوماتيكي (CI/CD)

يستخدم المشروع **GitHub Actions** مع مكتبة **`cx_Freeze`** و **`Inno Setup`** لعملية البناء المؤتمتة.
بمجرد رفع كود جديد إلى فرع `release`، ستقوم خوادم GitHub ببناء وإنتاج 6 ملفات مختلفة (نسخ تثبيت ونسخ محمولة للأنظمة الثلاثة) ورفعها تلقائياً.

---

## 🤝 المساهمة (Contributing)

نرحب بجميع المساهمات! سواء كان ذلك بإصلاح أخطاء، تحسين الأداء، إضافة أسئلة جديدة، أو تحسين دعم قارئات الشاشة.
1. قم بعمل Fork للمشروع.
2. قم بإنشاء فرع جديد (`git checkout -b feature/AmazingFeature`).
3. قم بتوثيق تعديلاتك (`git commit -m 'Add some AmazingFeature'`).
4. ارفع الفرع (`git push origin feature/AmazingFeature`).
5. افتح Pull Request للتقييم.

---

## 📄 حقوق النشر والترخيص (License)
هذا المشروع مفتوح المصدر. جميع الحقوق محفوظة © 2026 لـ [MesterPerfect](https://github.com/MesterPerfect). 
نسأل الله أن يجعل هذا العمل خالصاً لوجهه الكريم وأن ينفع به.