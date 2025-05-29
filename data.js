// data.js
const sections = {
    ar: {
        personal_data: {
            title: '👤 بيانات شخصية',
            fieldType: 'text',
            questions: ['ما هو اسمك؟', 'ما تاريخ ميلادك؟', 'ما هي جنسيتك؟', 'ما اللغات التي تتحدثها؟']
        },
        social_status: {
            title: '👥 الحالة الاجتماعية',
            fieldType: 'select',
            options: ['أعزب', 'متزوج', 'مطلق', 'أرمل'],
            questions: ['ما هي حالتك الاجتماعية؟', 'كيف تصف علاقاتك الأسرية؟', 'ما أهم العلاقات في حياتك؟']
        },
        edu_prof_background: {
            title: '🎓 الخلفية التعليمية/المهنية',
            fieldType: 'text',
            questions: ['ما هو مجال دراستك؟', 'ما هي الشهادات التي حصلت عليها؟', 'ما خبراتك المهنية؟', 'ما هي مهاراتك الرئيسية؟']
        },
        thinking_reference: {
            title: '💭 مرجعية التفكير',
            fieldType: 'select',
            options: ['عقلانية', 'حدسية', 'دينية', 'تجريبية'],
            questions: ['ما هي مرجعيتك الفكرية؟', 'هل تفضل التفكير العقلاني أم الحدسي؟', 'ما الذي يشكل أفكارك؟']
        },
        cognitive_passion: {
            title: '🔥 الشغف المعرفي',
            fieldType: 'text',
            questions: ['ما هو شغفك المعرفي؟', 'كيف تستكشف اهتماماتك الفكرية؟', 'ما الذي يلهمك للتعلم؟', 'ما هي المجالات التي تحب استكشافها؟']
        },
        ethical_values: {
            title: '⚖️ القيم الأخلاقية',
            fieldType: 'checkbox',
            options: ['العدل', 'الصدق', 'الرحمة', 'الاحترام', 'النزاهة', 'المسؤولية'],
            questions: ['ما هي القيم الأخلاقية الأكثر أهمية؟', 'كيف تطبق قيمك في حياتك؟', 'ما الذي يميز أخلاقياتك؟']
        },
        core_concepts_perspective: {
            title: '🌍 منظور المفاهيم الجوهرية',
            fieldType: 'text',
            questions: ['ما هي المفاهيم الجوهرية التي تؤمن بها؟', 'كيف تفسر الحرية؟', 'ما هو مفهوم الجمال بالنسبة لك؟', 'ما هي الحقيقة في نظرك؟']
        },
        cognitive_tools: {
            title: '🛠️ الأدوات المعرفية',
            fieldType: 'text',
            questions: ['ما هي الأدوات المعرفية التي تستخدمها؟', 'كيف تستخدم المنطق في قراراتك؟', 'ما هي أساليب التفكير التي تفضلها؟']
        },
        inspiring_figures: {
            title: '🌟 الشخصيات الملهمة',
            fieldType: 'text',
            questions: ['من هي الشخصية الملهمة بالنسبة لك؟', 'لماذا تعتبر هذه الشخصية مؤثرة؟', 'كيف أثرت عليك؟']
        },
        intellectual_sins: {
            title: '⚠️ الخطايا الفكرية',
            fieldType: 'checkbox',
            options: ['التحيز التأكيدي', 'الدوغماتية', 'التفكير الجماعي', 'التبسيط المفرط', 'التعميم المتسرع'],
            questions: ['ما التحيزات الفكرية التي تتجنبها؟', 'كيف تتعامل مع الدوغماتية؟', 'ما هي أخطاء التفكير الشائعة؟']
        },
        project_objective: {
            title: '📈 المشروع/الهدف',
            fieldType: 'text',
            questions: ['ما هو مشروعك الحالي؟', 'ما هي أهدافك المهنية؟', 'ما الذي تريد تحقيقه خلال 5 سنوات؟', 'كيف تخطط لمشروعك؟']
        },
        pivotal_example: {
            title: '📖 مثال محوري',
            fieldType: 'text',
            questions: ['ما هو المثال المحوري الذي أثر فيك؟', 'كيف شكل هذا المثال تفكيرك؟', 'ما القصة التي تريد مشاركتها؟']
        },
        causal_relations: {
            title: '🔗 العلاقات السببية',
            fieldType: 'text',
            questions: ['ما هي العلاقة السببية التي تراها بين الأفكار؟', 'كيف تربط بين المفاهيم؟', 'ما الذي يؤثر على قراراتك؟']
        },
        llm_persona: {
            title: '🤖 شخصية النموذج',
            fieldType: 'select',
            options: ['مساعد تحليلي', 'مستشار ودود', 'معلم', 'مفكر نقدي', 'مستكشف فضولي'],
            questions: ['ما هو الدور المفضل للنموذج؟', 'كيف تريد أن يكون النموذج مساعدًا؟', 'ما هي شخصية النموذج المثالية؟']
        },
        conceptual_tuning: {
            title: '⚙️ تهيئة المفاهيم',
            fieldType: 'text',
            questions: ['ما هي المصطلحات الخاصة التي تستخدمها؟', 'كيف تعرف مفاهيمك؟', 'ما الذي يميز لغتك الفكرية؟']
        },
        interaction_style: {
            title: '💬 أسلوب التفاعل',
            fieldType: 'select',
            options: ['تحليلي', 'ودود', 'موجز', 'تفصيلي', 'سقراطي'],
            questions: ['ما هو أسلوب التفاعل المفضل لديك؟', 'كيف تفضل التواصل؟', 'ما الذي يجعل التفاعل فعالًا؟']
        },
        intervention_level: {
            title: '🛑 مستوى التدخل',
            fieldType: 'select',
            options: ['استباقي', 'تفاعلي', 'أدنى (ملاحظ فقط)'],
            questions: ['ما هو مستوى التدخل المفضل؟', 'هل تفضل التدخل الاستباقي أم التفاعلي؟', 'كيف تتعامل مع النصائح؟']
        },
        alignment_level: {
            title: '🔄 مستوى التوافق',
            fieldType: 'text',
            questions: ['ما هو مستوى التوافق الفكري المطلوب؟', 'كيف تحقق التوافق مع الأفكار؟', 'ما الذي يعزز توافقك؟']
        },
        critique_mechanism: {
            title: '📝 آلية النقد',
            fieldType: 'text',
            questions: ['كيف تفضل تلقي النقد؟', 'ما هي شروط النقد البناء؟', 'كيف تستفيد من النقد؟']
        },
        prohibitions_warnings: {
            title: '🚫 المحظورات/التحذيرات',
            fieldType: 'text',
            questions: ['ما هي المحظورات التي تضعها؟', 'ما التحذيرات التي تهتم بها؟', 'كيف تتجنب المخاطر؟']
        },
        memory_directives: {
            title: '🧠 توجيهات الذاكرة',
            fieldType: 'text',
            questions: ['كيف تدير ذاكرتك؟', 'ما هي توجيهات السياق التي تفضلها؟', 'كيف تحتفظ بالمعلومات؟']
        },
        cognitive_preference: {
            title: '🧩 التفضيلات المعرفية',
            fieldType: 'checkbox',
            options: ['تحليلي', 'إبداعي', 'منطقي', 'عاطفي', 'حدسي', 'عملي'],
            questions: ['ما هي تفضيلاتك المعرفية؟', 'كيف تؤثر على قراراتك؟', 'ما الذي يميز تفكيرك؟']
        },
        mental_state: {
            title: '😊 الحالة الذهنية',
            fieldType: 'select',
            options: ['هادئ', 'متوتر', 'مركز', 'مشوش', 'متحفز', 'محبط'],
            questions: ['كيف تصف حالتك الذهنية؟', 'ما الذي يؤثر على تركيزك؟', 'كيف تحافظ على سلامتك العقلية؟']
        },
        sports_inclinations: {
            title: '⚽ الميول الرياضية',
            fieldType: 'checkbox',
            options: ['كرة القدم', 'الجري', 'السباحة', 'اليوغا', 'رياضات قتالية', 'لا شيء'],
            questions: ['ما هي ميولك الرياضية؟', 'ما الرياضات التي تمارسها؟', 'كيف تؤثر الرياضة عليك؟']
        },
        additional_notes: {
            title: '📝 ملاحظات إضافية',
            fieldType: 'text',
            questions: ['هل لديك ملاحظات إضافية؟', 'ما الذي تريد إضافته؟', 'هل هناك شيء آخر تود مشاركته؟']
        }
    },
    en: {
        personal_data: {
            title: '👤 Personal Data',
            fieldType: 'text',
            questions: ['What is your name?', 'What is your date of birth?', 'What is your nationality?', 'What languages do you speak?']
        },
        social_status: {
            title: '👥 Social Status',
            fieldType: 'select',
            options: ['Single', 'Married', 'Divorced', 'Widowed'],
            questions: ['What is your social status?', 'How would you describe your familial relationships?', 'What are the most important relationships in your life?']
        },
        edu_prof_background: {
            title: '🎓 Educational/Professional Background',
            fieldType: 'text',
            questions: ['What field of study did you pursue?', 'What certifications have you obtained?', 'What are your professional experiences?', 'What are your key skills?']
        },
        thinking_reference: {
            title: '💭 Thinking Reference',
            fieldType: 'select',
            options: ['Rational', 'Intuitive', 'Religious', 'Empirical'],
            questions: ['What is your thinking reference?', 'Do you prefer rational or intuitive thinking?', 'What shapes your thoughts?']
        },
        cognitive_passion: {
            title: '🔥 Cognitive Passion',
            fieldType: 'text',
            questions: ['What is your cognitive passion?', 'How do you explore your intellectual interests?', 'What inspires you to learn?', 'What fields do you love to explore?']
        },
        ethical_values: {
            title: '⚖️ Ethical Values',
            fieldType: 'checkbox',
            options: ['Justice', 'Honesty', 'Compassion', 'Respect', 'Integrity', 'Responsibility'],
            questions: ['What are your most important ethical values?', 'How do you apply your values in your life?', 'What distinguishes your ethics?']
        },
        core_concepts_perspective: {
            title: '🌍 Core Concepts Perspective',
            fieldType: 'text',
            questions: ['What core concepts do you believe in?', 'How do you interpret freedom?', 'What is the concept of beauty to you?', 'What is truth in your view?']
        },
        cognitive_tools: {
            title: '🛠️ Cognitive Tools',
            fieldType: 'text',
            questions: ['What cognitive tools do you use?', 'How do you use logic in your decisions?', 'What thinking methods do you prefer?']
        },
        inspiring_figures: {
            title: '🌟 Inspiring Figures',
            fieldType: 'text',
            questions: ['Who is an inspiring figure to you?', 'Why is this person influential?', 'How have they impacted you?']
        },
        intellectual_sins: {
            title: '⚠️ Intellectual Sins',
            fieldType: 'checkbox',
            options: ['Confirmation Bias', 'Dogmatism', 'Groupthink', 'Oversimplification', 'Hasty Generalization'],
            questions: ['What intellectual biases do you avoid?', 'How do you deal with dogmatism?', 'What are common thinking errors?']
        },
        project_objective: {
            title: '📈 Project/Objective',
            fieldType: 'text',
            questions: ['What is your current project?', 'What are your professional goals?', 'What do you want to achieve in five years?', 'How do you plan your project?']
        },
        pivotal_example: {
            title: '📖 Pivotal Example',
            fieldType: 'text',
            questions: ['What is a pivotal example that impacted you?', 'How did this example shape your thinking?', 'What story would you like to share?']
        },
        causal_relations: {
            title: '🔗 Causal Relations',
            fieldType: 'text',
            questions: ['What causal relationship do you see between ideas?', 'How do you connect concepts?', 'What influences your decisions?']
        },
        llm_persona: {
            title: '🤖 Model Persona',
            fieldType: 'select',
            options: ['Analytical Assistant', 'Friendly Advisor', 'Teacher', 'Critical Thinker', 'Curious Explorer'],
            questions: ['What is the preferred role for the model?', 'How do you want the model to assist you?', 'What is the ideal model persona?']
        },
        conceptual_tuning: {
            title: '⚙️ Conceptual Tuning',
            fieldType: 'text',
            questions: ['What specific terms do you use?', 'How do you define your concepts?', 'What distinguishes your intellectual language?']
        },
        interaction_style: {
            title: '💬 Interaction Style',
            fieldType: 'select',
            options: ['Analytical', 'Friendly', 'Concise', 'Detailed', 'Socratic'],
            questions: ['What is your preferred interaction style?', 'How do you like to communicate?', 'What makes interaction effective?']
        },
        intervention_level: {
            title: '🛑 Intervention Level',
            fieldType: 'select',
            options: ['Proactive', 'Reactive', 'Minimal (Observational)'],
            questions: ['What is your preferred intervention level?', 'Do you prefer proactive or reactive intervention?', 'How do you handle advice?']
        },
        alignment_level: {
            title: '🔄 Alignment Level',
            fieldType: 'text',
            questions: ['What is the required intellectual alignment level?', 'How do you achieve alignment with ideas?', 'What enhances your alignment?']
        },
        critique_mechanism: {
            title: '📝 Critique Mechanism',
            fieldType: 'text',
            questions: ['How do you prefer to receive criticism?', 'What are the conditions for constructive criticism?', 'How do you benefit from criticism?']
        },
        prohibitions_warnings: {
            title: '🚫 Prohibitions/Warnings',
            fieldType: 'text',
            questions: ['What prohibitions do you set?', 'What warnings are you concerned about?', 'How do you avoid risks?']
        },
        memory_directives: {
            title: '🧠 Memory Directives',
            fieldType: 'text',
            questions: ['How do you manage your memory?', 'What context directives do you prefer?', 'How do you retain information?']
        },
        cognitive_preference: {
            title: '🧩 Cognitive Preferences',
            fieldType: 'checkbox',
            options: ['Analytical', 'Creative', 'Logical', 'Emotional', 'Intuitive', 'Practical'],
            questions: ['What are your cognitive preferences?', 'How do they affect your decisions?', 'What distinguishes your thinking?']
        },
        mental_state: {
            title: '😊 Mental State',
            fieldType: 'select',
            options: ['Calm', 'Stressed', 'Focused', 'Confused', 'Motivated', 'Frustrated'],
            questions: ['How do you describe your mental state?', 'What affects your focus?', 'How do you maintain mental health?']
        },
        sports_inclinations: {
            title: '⚽ Sports Inclinations',
            fieldType: 'checkbox',
            options: ['Football', 'Running', 'Swimming', 'Yoga', 'Martial Arts', 'None'],
            questions: ['What are your sports inclinations?', 'What sports do you practice?', 'How does sport affect you?']
        },
        additional_notes: {
            title: '📝 Additional Notes',
            fieldType: 'text',
            questions: ['Do you have additional notes?', 'What would you like to add?', 'Is there anything else you’d like to share?']
        }
    }
};

const translations = {
    ar: {
        title: '🌌 هيباتيا - بروتوكول المستخدم',
        appVersion: 'هيباتيا الإصدار 1.0.0',
        inputPlaceholder: 'اكتب إجابتك هنا...',
        send: 'إرسال',
        skip: 'تخطي',
        export: 'تصدير كـ JSON',
        exported: 'تم التصدير بنجاح!',
        save: 'حفظ',
        saved: 'تم الحفظ بنجاح!',
        import: 'استيراد',
        imported: 'تم الاستيراد بنجاح!',
        importError: 'خطأ أثناء الاستيراد! تأكد أن الملف JSON صالح وبالهيكل الصحيح.',
        editAnswers: 'تحرير الإجابات',
        noAnswers: 'لا توجد إجابات لتحريرها!',
        editSaved: 'تم حفظ التعديلات!',
        noAnswer: 'يرجى كتابة إجابة!',
        skippedQuestions: 'الأسئلة المتخطاة', // تم تعديل النص قليلاً
        skippedQuestionsTitle: 'قائمة الأسئلة المتخطاة',
        skippedList: 'الأسئلة التي تم تخطيها: ',
        noSkipped: 'لا توجد أسئلة تم تخطيها!',
        retrySkipped: 'إعادة محاولة سؤال متخطى', // تم تعديل النص
        report: 'عرض التقرير النهائي',
        reportTitle: 'التقرير النهائي',
        userGuide: 'دليل المستخدم',
        userGuideText: `مرحباً بك في بروتوكول هيباتيا!
- أجب على الأسئلة المطروحة في صندوق الدردشة.
- يمكنك تخطي الأسئلة باستخدام زر "تخطي".
- استخدم القائمة لتصدير/استيراد الإجابات أو تحريرها.
- التقرير النهائي يُظهر جميع إجاباتك.
- لتغيير اللغة، استخدم خيار "تغيير اللغة" في القائمة.
- يمكنك عرض وإعادة محاولة الأسئلة المتخطاة من القائمة.`,
        reset: 'إعادة تعيين',
        resetConfirm: 'هل أنت متأكد من إعادة تعيين جميع الإجابات وبيانات التقدم؟',
        endOfQuestions: 'انتهت الأسئلة الأساسية! سأطرح الآن أسئلة إضافية بناءً على إجاباتك وتفاعلاتك.',
        language: 'تغيير اللغة',
        darkMode: 'الوضع الليلي',
        lightMode: 'الوضع النهاري',
        editModalTitle: 'تحرير الإجابة',
        editModalSave: 'حفظ التعديل',
        editModalCancel: 'إلغاء',
        languageModalTitle: 'اختر اللغة',
        languageModalSave: 'حفظ اللغة',
        languageModalCancel: 'إلغاء',
        reportModalClose: 'إغلاق التقرير',
        guideModalClose: 'إغلاق الدليل',
        loading: 'جار التحميل...',
        confirmAction: 'تأكيد الإجراء', // للنافذة المنبثقة العامة للتأكيد
        confirmButton: 'تأكيد',
        cancelButton: 'إلغاء',
        genericError: 'حدث خطأ ما. يرجى المحاولة مرة أخرى.',
        invalidDataFormat: "تنسيق البيانات غير صالح."
    },
    en: {
        title: '🌌 Hypatia - User Protocol',
        appVersion: 'Hypatia v1.0.0',
        inputPlaceholder: 'Type your answer here...',
        send: 'Send',
        skip: 'Skip',
        export: 'Export as JSON',
        exported: 'Exported successfully!',
        save: 'Save',
        saved: 'Saved successfully!',
        import: 'Import',
        imported: 'Imported successfully!',
        importError: 'Error during import! Ensure the file is valid JSON with the correct structure.',
        editAnswers: 'Edit Answers',
        noAnswers: 'No answers available to edit!',
        editSaved: 'Edits saved!',
        noAnswer: 'Please enter an answer!',
        skippedQuestions: 'Skipped Questions', // Slightly modified text
        skippedQuestionsTitle: 'List of Skipped Questions',
        skippedList: 'Skipped questions: ',
        noSkipped: 'No questions were skipped!',
        retrySkipped: 'Retry a Skipped Question', // Modified text
        report: 'View Final Report',
        reportTitle: 'Final Report',
        userGuide: 'User Guide',
        userGuideText: `Welcome to Hypatia's Protocol!
- Answer the questions presented in the chat box.
- You can skip questions using the "Skip" button.
- Use the menu to export/import answers or edit them.
- The final report displays all your answers.
- To change the language, use the "Change Language" option in the menu.
- You can view and retry skipped questions from the menu.`,
        reset: 'Reset',
        resetConfirm: 'Are you sure you want to reset all answers and progress data?',
        endOfQuestions: 'Basic questions are complete! I’ll now ask additional questions based on your answers and interactions.',
        language: 'Change Language',
        darkMode: 'Dark Mode',
        lightMode: 'Light Mode',
        editModalTitle: 'Edit Answer',
        editModalSave: 'Save Edit',
        editModalCancel: 'Cancel',
        languageModalTitle: 'Select Language',
        languageModalSave: 'Save Language',
        languageModalCancel: 'Cancel',
        reportModalClose: 'Close Report',
        guideModalClose: 'Close Guide',
        loading: 'Loading...',
        confirmAction: 'Confirm Action', // For generic confirm modal
        confirmButton: 'Confirm',
        cancelButton: 'Cancel',
        genericError: 'An error occurred. Please try again.',
        invalidDataFormat: "Invalid data format."
    }
};