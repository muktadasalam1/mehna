    // Language toggle with translations
    (function() {
      var translations = {
        'nav-platform': { en: 'Platform', ar: 'المنصة' },
        'nav-trust': { en: 'Trust', ar: 'الثقة' },
        'nav-stories': { en: 'Stories', ar: 'قصص النجاح' },
        'nav-pricing': { en: 'Pricing', ar: 'الأسعار' },
        'nav-cta': { en: 'Get Started', ar: 'ابدأ الآن' },
        'nav-switch': { en: 'Main Menu', ar: 'القائمة الرئيسية' },
        'hero-badge': { en: 'Trusted employment marketplace in Iraq', ar: 'منصة التوظيف الموثوقة في العراق' },
        'hero-title': { en: "Iraq's Direct Gateway to Opportunity", ar: 'بوابتك المباشرة للفرص في العراق' },
        'hero-desc': { en: 'Mehna connects verified Iraqi talent with trusted employers across corporate and trade sectors — with one-click applications, real-time status tracking, and rigorous verification.', ar: 'تربط مِهنة الكفاءات العراقية الموثّقة بأصحاب العمل الموثوقين في القطاعات المهنية والحرفية — مع تقديم بنقرة واحدة، وتتبّع فوري للحالة، وتحقّق دقيق.' },
        'hero-btn1': { en: 'Find Your Next Role', ar: 'ابحث عن وظيفتك القادمة' },
        'hero-btn2': { en: 'Post a Verified Job', ar: 'انشر وظيفة موثّقة' },
        'stat-seekers': { en: 'Verified seekers', ar: 'باحث موثّق' },
        'stat-employers': { en: 'Trusted employers', ar: 'صاحب عمل موثوق' },
        'stat-placements': { en: 'Placements made', ar: 'عملية توظيف' },
        'ticker-live': { en: 'Live', ar: 'مباشر' },
        'ecosystem-tag': { en: 'The Ecosystem', ar: 'المنظومة' },
        'ecosystem-title': { en: 'Built for both sides of hiring', ar: 'مصمّمة لطرفي عملية التوظيف' },
        'ecosystem-desc': { en: 'Two tailored workflows — one trusted platform connecting seekers and employers across Iraq.', ar: 'مساران مخصّصان — منصة واحدة موثوقة تربط الباحثين وأصحاب العمل في جميع أنحاء العراق.' },
        'seekers-tag': { en: 'For Job Seekers', ar: 'للباحثين عن عمل' },
        'seekers-title': { en: 'Land verified roles faster', ar: 'احصل على وظائف موثّقة أسرع' },
        'seekers-1-title': { en: 'One-click applications', ar: 'تقديم بنقرة واحدة' },
        'seekers-1-desc': { en: 'Apply to any verified role instantly with your saved Mehna profile.', ar: 'قدّم على أي وظيفة موثّقة فوراً باستخدام ملفك المحفوظ في مِهنة.' },
        'seekers-2-title': { en: 'Real-time status tracking', ar: 'تتبّع الحالة الفوري' },
        'seekers-2-desc': { en: 'See exactly where you stand — viewed, shortlisted, or interview stage.', ar: 'اعرف موقعك بدقة — تمت المشاهدة، القائمة المختصرة، أو مرحلة المقابلة.' },
        'seekers-3-title': { en: 'Smart role alerts', ar: 'تنبيهات وظيفية ذكية' },
        'seekers-3-desc': { en: 'Get matched notifications the moment a fitting verified job is posted.', ar: 'استلم إشعارات مطابقة لحظة نشر وظيفة موثّقة تناسبك.' },
        'employers-tag': { en: 'For Employers', ar: 'لأصحاب العمل' },
        'employers-title': { en: 'Hire trusted talent with confidence', ar: 'وظّف كفاءات موثوقة بثقة' },
        'employers-1-title': { en: 'Candidate pipeline', ar: 'مسار المرشّحين' },
        'employers-1-desc': { en: 'Manage applicants through a clean visual hiring pipeline dashboard.', ar: 'أدر المتقدمين عبر لوحة مسار توظيف مرئية ومنظّمة.' },
        'employers-2-title': { en: 'Verification badge', ar: 'شارة التوثيق' },
        'employers-2-desc': { en: 'Earn a verified employer badge that builds instant candidate trust.', ar: 'احصل على شارة صاحب عمل موثوق تبني ثقة فورية لدى المرشّحين.' },
        'employers-3-title': { en: 'Precision filtering', ar: 'تصفية دقيقة' },
        'employers-3-desc': { en: 'Filter by skill, sector, city, and verification level in seconds.', ar: 'صفِّ حسب المهارة والقطاع والمدينة ومستوى التوثيق خلال ثوانٍ.' },
        'trust-tag': { en: 'Trust & Verification', ar: 'الثقة والتوثيق' },
        'trust-title': { en: 'A vetting process you can rely on', ar: 'عملية تحقّق يمكنك الاعتماد عليها' },
        'trust-desc': { en: 'Every profile and employer passes a rigorous, human-reviewed pipeline before earning a verified badge — so trust is never assumed, it is earned.', ar: 'يمر كل ملف وصاحب عمل عبر سلسلة تحقّق صارمة يراجعها بشر قبل الحصول على شارة التوثيق — فالثقة لا تُفترض، بل تُكتسب.' },
        'trust-1': { en: 'Identity check', ar: 'التحقق من الهوية' },
        'trust-1-desc': { en: 'Government-ID matching confirms every person is real and unique.', ar: 'مطابقة الهوية الرسمية تؤكد أن كل شخص حقيقي وفريد.' },
        'trust-2': { en: 'Document review', ar: 'مراجعة المستندات' },
        'trust-2-desc': { en: 'Credentials, licenses, and business registrations are manually reviewed.', ar: 'تتم مراجعة الشهادات والتراخيص والسجلات التجارية يدوياً.' },
        'trust-3': { en: 'Admin approval', ar: 'موافقة الإدارة' },
        'trust-3-desc': { en: 'A Mehna specialist signs off before any verified badge is granted.', ar: 'يعتمد أخصائي مِهنة الملف قبل منح أي شارة توثيق.' },
        'trust-4': { en: 'Ongoing monitoring', ar: 'مراقبة مستمرة' },
        'trust-4-desc': { en: 'Continuous integrity checks keep the marketplace safe and trusted.', ar: 'فحوصات نزاهة مستمرة تحافظ على أمان المنصة وثقتها.' },
        'analytics-label': { en: 'Platform Analytics', ar: 'تحليلات المنصة' },
        'analytics-title': { en: 'Placements this week', ar: 'التوظيفات هذا الأسبوع' },
        'stat-verified': { en: 'Verified', ar: 'موثّق' },
        'stat-encryption': { en: 'Encryption', ar: 'تشفير' },
        'stat-vetting': { en: 'Vetting', ar: 'التحقق' },
        'soc-title': { en: 'SOC-2 Aligned', ar: 'متوافق مع SOC-2' },
        'soc-desc': { en: 'Data secured', ar: 'بيانات مؤمّنة' },
        'stories-tag': { en: 'Success Stories', ar: 'قصص النجاح' },
        'stories-title': { en: 'Real hiring transformations', ar: 'قصص توظيف حقيقية' },
        'stories-desc': { en: 'From corporate offices to skilled trades — Iraqi talent finding trusted opportunity through Mehna.', ar: 'من المكاتب المؤسسية إلى الحرف المهارية — كفاءات عراقية تجد فرصاً موثوقة عبر مِهنة.' },
        'story1-name': { en: 'Zainab Al-Karim', ar: 'زينب الكريم' },
        'story1-role': { en: 'Software Developer · Hired at NovaTech Baghdad', ar: 'مطوّرة برمجيات · تم توظيفها في نوفاتك بغداد' },
        'story1-quote': { en: 'I applied with one click and tracked every step. Within eight days I signed with a verified company I could actually trust.', ar: 'قدّمت بنقرة واحدة وتتبّعت كل خطوة. خلال ثمانية أيام وقّعت مع شركة موثّقة أثق بها فعلاً.' },
        'story2-name': { en: 'Omar Haddad', ar: 'عمر حدّاد' },
        'story2-role': { en: 'Civil Engineer · Hired at Rafidain Build', ar: 'مهندس مدني · تم توظيفه في الرافدين للإنشاءات' },
        'story2-quote': { en: 'The verification badge made all the difference. Employers reached out to me because my credentials were already trusted.', ar: 'أحدثت شارة التوثيق فرقاً كبيراً. تواصل معي أصحاب العمل لأن مؤهلاتي كانت موثوقة مسبقاً.' },
        'story3-name': { en: 'Karrar Jassim', ar: 'كرار جاسم' },
        'story3-role': { en: 'Master Electrician · Hired at Basra Power Co.', ar: 'كهربائي خبير · تم توظيفه في شركة البصرة للطاقة' },
        'story3-quote': { en: 'As a tradesman, I never had a platform that took my skills seriously. Mehna connected me to real, verified work.', ar: 'كحرفي، لم أجد يوماً منصة تأخذ مهاراتي على محمل الجد. مِهنة ربطتني بعمل حقيقي وموثّق.' },
        'logos-label': { en: 'Trusted by verified Iraqi companies', ar: 'موثوقة من شركات عراقية معتمدة' },
        'pricing-tag': { en: 'Plans', ar: 'الخطط' },
        'pricing-title': { en: 'Choose your path forward', ar: 'اختر مسارك نحو الأمام' },
        'pricing-desc': { en: 'Start free and upgrade when you are ready to stand out.', ar: 'ابدأ مجاناً وترقَّ عندما تكون مستعداً للتميّز.' },
        'plan-free': { en: 'Free', ar: 'مجاني' },
        'plan-free-period': { en: '/ forever', ar: '/ للأبد' },
        'plan-free-desc': { en: 'For seekers getting started.', ar: 'للباحثين في بداية الطريق.' },
        'plan-free-1': { en: 'Create a verified profile', ar: 'إنشاء ملف موثّق' },
        'plan-free-2': { en: 'Apply to open roles', ar: 'التقديم على الوظائف المتاحة' },
        'plan-free-3': { en: 'Basic status tracking', ar: 'تتبّع الحالة الأساسي' },
        'plan-free-4': { en: 'Community support', ar: 'دعم المجتمع' },
        'plan-free-btn': { en: 'Find Your Next Role', ar: 'ابحث عن وظيفتك القادمة' },
        'plan-pro': { en: 'Pro', ar: 'برو' },
        'plan-pro-badge': { en: 'Most popular', ar: 'الأكثر شيوعاً' },
        'plan-pro-period': { en: '/ month', ar: '/ شهرياً' },
        'plan-pro-desc': { en: 'For serious talent and hiring employers.', ar: 'للكفاءات الجادة وأصحاب العمل.' },
        'plan-pro-1': { en: 'Everything in Free', ar: 'كل ما في الخطة المجانية' },
        'plan-pro-2': { en: 'Priority verified badge', ar: 'شارة توثيق ذات أولوية' },
        'plan-pro-3': { en: 'Featured profile & job posts', ar: 'ملف ووظائف مميّزة' },
        'plan-pro-4': { en: 'Advanced pipeline & analytics', ar: 'مسار وتحليلات متقدمة' },
        'plan-pro-5': { en: 'Real-time smart alerts', ar: 'تنبيهات ذكية فورية' },
        'plan-pro-6': { en: 'Dedicated account manager', ar: 'مدير حساب مخصّص' },
        'plan-pro-btn': { en: 'Post a Verified Job', ar: 'انشر وظيفة موثّقة' },
        'cta-title': { en: 'Your next opportunity starts on Mehna', ar: 'فرصتك القادمة تبدأ على مِهنة' },
        'cta-desc': { en: 'Join thousands of verified Iraqi professionals and employers building the future of work — together.', ar: 'انضم إلى آلاف المحترفين وأصحاب العمل العراقيين الموثّقين وهم يبنون مستقبل العمل — معاً.' },
        'cta-btn1': { en: 'Find Your Next Role', ar: 'ابحث عن وظيفتك القادمة' },
        'cta-btn2': { en: 'Post a Verified Job', ar: 'انشر وظيفة موثّقة' },
        'footer-desc': { en: "Iraq's trusted bilingual employment marketplace connecting verified talent with opportunity.", ar: 'منصة التوظيف العراقية الموثوقة ثنائية اللغة التي تربط الكفاءات الموثّقة بالفرص.' },
        'footer-platform': { en: 'Platform', ar: 'المنصة' },
        'footer-company': { en: 'Company', ar: 'الشركة' },
        'footer-legal': { en: 'Legal', ar: 'قانوني' },
        'footer-copyright': { en: '© 2026 Mehna. All rights reserved.', ar: '© 2026 مِهنة. جميع الحقوق محفوظة.' },
        'footer-made': { en: 'Made in Iraq · صُنع في العراق', ar: 'صُنع في العراق · Made in Iraq' }
      };

      var langBtn = document.getElementById('lang-btn');
      var isArabic = localStorage.getItem('mehna-lang') === 'ar';

      function applyLang(arabic) {
        isArabic = arabic;
        var html = document.documentElement;
        html.lang = arabic ? 'ar' : 'en';
        html.dir = arabic ? 'rtl' : 'ltr';
        langBtn.textContent = arabic ? 'EN' : 'العربية';
        localStorage.setItem('mehna-lang', arabic ? 'ar' : 'en');

        var els = document.querySelectorAll('[data-key]');
        for (var i = 0; i < els.length; i++) {
          var key = els[i].getAttribute('data-key');
          if (translations[key]) {
            els[i].textContent = arabic ? translations[key].ar : translations[key].en;
          }
        }
      }

      langBtn.addEventListener('click', function() {
        applyLang(!isArabic);
      });

      // Apply stored language on load
      if (isArabic) {
        applyLang(true);
      }
    })();

    // Scroll header
    (function() {
      var header = document.getElementById('site-header');
      function onScroll() {
        if (window.scrollY > 12) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      }
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    })();

    // Theme toggle
    (function() {
      var btn = document.getElementById('theme-toggle');
      var moon = document.getElementById('theme-icon-moon');
      var sun = document.getElementById('theme-icon-sun');
      var isDark = false;
      btn.addEventListener('click', function() {
        isDark = !isDark;
        document.documentElement.classList.toggle('dark', isDark);
        moon.style.display = isDark ? 'none' : 'block';
        sun.style.display = isDark ? 'block' : 'none';
      });
    })();

    // Mobile menu toggle
    (function() {
      var toggle = document.getElementById('mobile-toggle');
      var menu = document.getElementById('mobile-menu');
      toggle.addEventListener('click', function() {
        menu.classList.toggle('open');
      });
      var links = menu.querySelectorAll('a');
      for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function() {
          menu.classList.remove('open');
        });
      }
    })();

    // Trust steps accordion
    (function() {
      var steps = document.querySelectorAll('.trust-step');
      for (var i = 0; i < steps.length; i++) {
        steps[i].addEventListener('click', function() {
          for (var j = 0; j < steps.length; j++) {
            steps[j].classList.remove('active');
            steps[j].querySelector('.trust-step-icon').classList.remove('active');
            steps[j].querySelector('.trust-step-icon').classList.add('inactive');
          }
          this.classList.add('active');
          this.querySelector('.trust-step-icon').classList.remove('inactive');
          this.querySelector('.trust-step-icon').classList.add('active');
        });
      }
    })();
  </script>
</body>
