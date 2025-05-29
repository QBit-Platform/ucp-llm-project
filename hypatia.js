// hypatia.js
document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const appTitle = document.querySelector('.app-header h2');
    const appVersionDisplay = document.getElementById('app-version');
    const chatBox = document.getElementById('chat-box');
    const inputContainer = document.getElementById('input-container');
    // sendButton and skipButton will be created dynamically within inputContainer
    const exportButton = document.getElementById('export-button');
    const saveButton = document.getElementById('save-button');
    const importButton = document.getElementById('import-button');
    const editAnswersButton = document.getElementById('edit-answers-button');
    const skippedQuestionsButton = document.getElementById('skipped-questions-button');
    // const retrySkippedButton = document.getElementById('retry-skipped-button'); // Will be handled within skipped questions modal
    const reportButton = document.getElementById('report-button');
    const userGuideButton = document.getElementById('user-guide-button');
    const resetButton = document.getElementById('reset-button');
    const darkModeButton = document.getElementById('dark-mode-button');
    const menuButton = document.getElementById('menu-button');
    const menu = document.getElementById('menu');
    const languageButton = document.getElementById('language-button');
    const importInput = document.getElementById('import-input');
    const alertBox = document.getElementById('alert-box');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Modal Elements (Generic Modal)
    const genericModal = document.getElementById('generic-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBodyContent = document.getElementById('modal-body-content');
    const modalFooterButtons = document.getElementById('modal-footer-buttons');
    const modalCloseButtons = document.querySelectorAll('.modal-close-button'); // For multiple close buttons if any

    // State Variables
    let currentLanguage = localStorage.getItem('hypatiaLanguage') || 'ar';
    let currentSectionKey = null; // Will hold the key of the current section
    let currentQuestionIndex = 0;
    let userAnswers = JSON.parse(localStorage.getItem('userAnswers')) || {};
    let lastAskedQuestionText = null; // Store the text of the last asked question
    let lastAskedQuestionCategory = null; // Store the category of the last asked question
    let followUpMode = false;
    let recentCategories = []; // Tracks recently asked categories to avoid quick repetition
    let autoExported = false;
    const userId = 'user_' + (localStorage.getItem('hypatiaUserId') || Math.random().toString(36).substr(2, 9));
    if (!localStorage.getItem('hypatiaUserId')) {
        localStorage.setItem('hypatiaUserId', userId.split('_')[1]);
    }

    let categoryUsage = JSON.parse(localStorage.getItem('categoryUsage')) || {};
    let categoryPriority = JSON.parse(localStorage.getItem('categoryPriority')) || {};
    let totalAnswersGiven = Object.keys(userAnswers).filter(q => userAnswers[q] && !userAnswers[q].startsWith('[')).length;

    // Dynamic Input Elements (will be created and managed)
    let currentInputElement = null;
    let sendButtonElement = null;
    let skipButtonElement = null;


    // --- INITIALIZATION ---
    function initializeApp() {
        document.documentElement.lang = currentLanguage;
        document.documentElement.dir = currentLanguage === 'ar' ? 'rtl' : 'ltr';
        initializeCategoryStates();
        updateInterfaceLanguage(); // This will also set button texts
        createInputControls(); // Create initial input controls
        loadChatHistory();
        askQuestion();

        // Dark mode persistence
        if (localStorage.getItem('hypatiaDarkMode') === 'true') {
            document.body.classList.add('dark-mode');
            updateDarkModeButtonText();
        }
    }

    function initializeCategoryStates() {
        const sectionKeys = Object.keys(sections[currentLanguage] || sections.en); // Fallback to English sections if current lang unavailable
        sectionKeys.forEach(key => {
            if (!categoryUsage[key]) {
                categoryUsage[key] = { count: 0, lastUsedAtTotalAnswers: 0 };
            }
            if (categoryPriority[key] === undefined) { // Check for undefined to allow 0 as a valid priority
                categoryPriority[key] = 1; // Default priority
            }
        });
        saveCategoryStates();
    }

    function saveCategoryStates() {
        localStorage.setItem('categoryUsage', JSON.stringify(categoryUsage));
        localStorage.setItem('categoryPriority', JSON.stringify(categoryPriority));
    }

    function loadChatHistory() {
        // A more sophisticated approach would be to store chat history separately
        // For now, re-add messages based on userAnswers
        chatBox.innerHTML = ''; // Clear existing
        const answeredQuestions = Object.keys(userAnswers);

        // Try to reconstruct the order, this is an approximation
        const allQuestionsInOrder = [];
        Object.keys(sections[currentLanguage] || sections.en).forEach(sectionKey => {
            sections[currentLanguage][sectionKey].questions.forEach(qText => {
                allQuestionsInOrder.push({text: qText, sectionKey: sectionKey});
            });
        });

        allQuestionsInOrder.forEach(qInfo => {
            if (userAnswers[qInfo.text]) {
                addMessage(qInfo.text, 'hypatia-message', sections[currentLanguage][qInfo.sectionKey].title);
                if (!userAnswers[qInfo.text].startsWith('[')) { // Not skipped
                    addMessage(userAnswers[qInfo.text], 'user-message');
                }
            }
        });
         // Add any answers for questions not in the current sections (e.g., generated or from different lang)
        answeredQuestions.forEach(qText => {
            if (!allQuestionsInOrder.some(q => q.text === qText)) {
                if (userAnswers[qText]) {
                    addMessage(qText, 'hypatia-message'); // No section title for these
                     if (!userAnswers[qText].startsWith('[')) {
                        addMessage(userAnswers[qText], 'user-message');
                    }
                }
            }
        });
    }


    // --- UI UPDATES & MESSAGING ---
    function updateInterfaceLanguage() {
        const lang = currentLanguage;
        document.documentElement.lang = lang;
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

        appTitle.textContent = translations[lang].title;
        appVersionDisplay.textContent = translations[lang].appVersion;

        // Update menu button texts using data-translate attribute
        menu.querySelectorAll('button span[data-translate]').forEach(span => {
            const key = span.getAttribute('data-translate');
            if (translations[lang][key]) {
                span.textContent = translations[lang][key];
            }
        });
        updateDarkModeButtonText(); // Special case for dark mode button text
    }

    function updateDarkModeButtonText() {
         const lang = currentLanguage;
        const isDarkMode = document.body.classList.contains('dark-mode');
        const darkModeButtonSpan = darkModeButton.querySelector('span');
        if(darkModeButtonSpan) {
            darkModeButtonSpan.textContent = isDarkMode ? translations[lang].lightMode : translations[lang].darkMode;
        }
    }


    function addMessage(text, className, sectionTitle = '') {
        if (sectionTitle && (!chatBox.lastElementChild || !chatBox.lastElementChild.classList.contains('section-title') || chatBox.lastElementChild.textContent !== sectionTitle)) {
            const titleDiv = document.createElement('div');
            titleDiv.className = 'section-title';
            titleDiv.textContent = sectionTitle;
            chatBox.appendChild(titleDiv);
        }
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function showAlert(text, type = 'success', duration = 3000) {
        alertBox.textContent = text;
        alertBox.className = ''; // Clear existing classes
        alertBox.classList.add(type); // 'success' or 'error'
        alertBox.style.display = 'block';
        setTimeout(() => {
            alertBox.style.display = 'none';
        }, duration);
    }

    function toggleLoading(show) {
        loadingIndicator.style.display = show ? 'flex' : 'none'; // Use flex for centering
    }

    // --- MODAL MANAGEMENT ---
    function openModal(titleKey, bodyHTML, footerButtonsConfig = []) {
        modalTitle.textContent = translations[currentLanguage][titleKey] || titleKey;
        modalBodyContent.innerHTML = bodyHTML;
        modalFooterButtons.innerHTML = ''; // Clear previous buttons

        footerButtonsConfig.forEach(btnConfig => {
            const button = document.createElement('button');
            button.id = btnConfig.id;
            button.className = btnConfig.className || 'action-button';
            button.textContent = translations[currentLanguage][btnConfig.textKey] || btnConfig.textKey;
            if (btnConfig.onClick) {
                // Remove previous listener if any to avoid multiple fires, especially for dynamic buttons
                const oldButton = document.getElementById(btnConfig.id);
                if(oldButton) {
                    const newButton = oldButton.cloneNode(true);
                    oldButton.parentNode.replaceChild(newButton, oldButton);
                    newButton.addEventListener('click', btnConfig.onClick);
                } else {
                     button.addEventListener('click', btnConfig.onClick);
                }
            }
            modalFooterButtons.appendChild(button);
        });

        genericModal.style.display = 'flex';
    }

    function closeModal() {
        genericModal.style.display = 'none';
        modalBodyContent.innerHTML = ''; // Clean up
        modalFooterButtons.innerHTML = '';
    }
    modalCloseButtons.forEach(btn => btn.addEventListener('click', closeModal));
    // Close modal if backdrop is clicked
    genericModal.addEventListener('click', (event) => {
        if (event.target === genericModal) {
            closeModal();
        }
    });


    // --- DYNAMIC INPUT HANDLING ---
    function createInputControls() {
        inputContainer.innerHTML = ''; // Clear previous controls

        currentInputElement = document.createElement('input'); // Default to text
        currentInputElement.type = 'text';
        currentInputElement.id = 'hypatia-input-box';
        currentInputElement.className = 'input-box';
        currentInputElement.placeholder = translations[currentLanguage].inputPlaceholder;
        currentInputElement.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') handleSendAnswer();
        });

        sendButtonElement = document.createElement('button');
        sendButtonElement.id = 'hypatia-send-button';
        sendButtonElement.className = 'action-button';
        sendButtonElement.textContent = translations[currentLanguage].send;
        sendButtonElement.addEventListener('click', handleSendAnswer);

        skipButtonElement = document.createElement('button');
        skipButtonElement.id = 'hypatia-skip-button';
        skipButtonElement.className = 'action-button';
        skipButtonElement.style.backgroundColor = 'var(--skip-button-bg)'; // Use CSS var
        skipButtonElement.textContent = translations[currentLanguage].skip;
        skipButtonElement.addEventListener('click', handleSkipQuestion);

        inputContainer.appendChild(currentInputElement);
        inputContainer.appendChild(sendButtonElement);
        inputContainer.appendChild(skipButtonElement);
    }

    function setupDynamicInput(fieldType, options = []) {
        inputContainer.innerHTML = ''; // Clear for new input type

        if (fieldType === 'select') {
            currentInputElement = document.createElement('select');
            currentInputElement.className = 'dynamic-input';
            options.forEach(optionText => {
                const opt = document.createElement('option');
                opt.value = optionText;
                opt.textContent = optionText;
                currentInputElement.appendChild(opt);
            });
        } else if (fieldType === 'checkbox') {
            currentInputElement = document.createElement('div');
            currentInputElement.className = 'dynamic-input';
            options.forEach(optionText => {
                const label = document.createElement('label');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = optionText;
                const textNode = document.createTextNode(' ' + optionText); // Add space
                label.appendChild(checkbox);
                label.appendChild(textNode);
                currentInputElement.appendChild(label);
            });
        } else { // Default to text
            currentInputElement = document.createElement('input');
            currentInputElement.type = 'text';
            currentInputElement.className = 'input-box'; // Re-use input-box class
            currentInputElement.placeholder = translations[currentLanguage].inputPlaceholder;
        }
        currentInputElement.id = 'hypatia-dynamic-input'; // Consistent ID for dynamic part
        currentInputElement.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && fieldType !== 'checkbox') handleSendAnswer(); // Enter for select/text
        });


        inputContainer.appendChild(currentInputElement);
        inputContainer.appendChild(sendButtonElement); // Re-append existing send/skip
        inputContainer.appendChild(skipButtonElement);

        if (currentInputElement.focus) currentInputElement.focus();
    }

    function getDynamicInputValue() {
        if (!currentInputElement) return '';
        if (currentInputElement.tagName === 'SELECT') {
            return currentInputElement.value;
        } else if (currentInputElement.tagName === 'DIV') { // Checkbox container
            const checkboxes = currentInputElement.querySelectorAll('input[type="checkbox"]:checked');
            return Array.from(checkboxes).map(cb => cb.value).join(', ');
        } else { // Input text
            return currentInputElement.value.trim();
        }
    }


    // --- QUESTION & ANSWER LOGIC ---
    function categorizeQuestionText(questionText) { // Renamed from categorizeQuestion
        const activeCategories = sections[currentLanguage] || sections.en;
        for (const [categoryKey, categoryData] of Object.entries(activeCategories)) {
            // Check against title first, then keywords if defined, then question text itself for broad match
            if (categoryData.title && categoryData.title.toLowerCase().includes(questionText.substring(0,10).toLowerCase())) return categoryKey;

            const keywords = categoryData.keywords || []; // Assuming you might add keywords to data.js later
            if (keywords.some(keyword => questionText.toLowerCase().includes(keyword.toLowerCase()))) {
                return categoryKey;
            }
            // Fallback: check if the question is one of this category's questions
            if (categoryData.questions && categoryData.questions.includes(questionText)) {
                return categoryKey;
            }
        }
        // Attempt to match keywords from the general `categories` object (if it were still used)
        // This part needs to be adapted if you have a new keyword source in data.js or remove it
        const generalCategorization = {
            ar: { personal_data: ['اسم', 'ميلاد', 'جنسية'], /* ... other categories ... */ },
            en: { personal_data: ['name', 'birth', 'nationality'], /* ... other categories ... */ }
        };
        const langCategories = generalCategorization[currentLanguage] || generalCategorization.en;
        for (const [category, keywords] of Object.entries(langCategories)) {
            if (keywords.some(keyword => questionText.toLowerCase().includes(keyword.toLowerCase()))) {
                return category;
            }
        }
        return 'general'; // Default category
    }

    function isPositiveAnswer(answer) {
        const positiveWords = translations[currentLanguage].positiveAnswerWords || // Get from translations if defined
            (currentLanguage === 'ar' ? ['نعم', 'بالطبع', 'أكيد', 'صحيح', 'أوافق', 'تمام'] : ['yes', 'sure', 'of course', 'definitely', 'agree', 'indeed']);
        return positiveWords.some(word => answer.toLowerCase().includes(word.toLowerCase()));
    }

    function updateCategoryPriorities(answerText, categoryKey) {
        // Simple example rules, can be expanded in data.js or here
        const rules = {
            ar: [
                { keyword: 'فلسفة', sourceCategory: 'cognitive_passion', boostCategories: ['thinking_reference', 'core_concepts_perspective'], factor: 1.5 },
                { keyword: 'قيادة', sourceCategory: 'project_objective', boostCategories: ['edu_prof_background', 'inspiring_figures'], factor: 1.3 },
                { keyword: 'تعلم', sourceCategory: 'cognitive_passion', boostCategories: ['cognitive_tools', 'edu_prof_background'], factor: 1.2 }
            ],
            en: [
                { keyword: 'philosophy', sourceCategory: 'cognitive_passion', boostCategories: ['thinking_reference', 'core_concepts_perspective'], factor: 1.5 },
                { keyword: 'leadership', sourceCategory: 'project_objective', boostCategories: ['edu_prof_background', 'inspiring_figures'], factor: 1.3 },
                { keyword: 'learn', sourceCategory: 'cognitive_passion', boostCategories: ['cognitive_tools', 'edu_prof_background'], factor: 1.2 }
            ]
        };
        const langRules = rules[currentLanguage] || rules.en;
        langRules.forEach(rule => {
            if (categoryKey === rule.sourceCategory && answerText.toLowerCase().includes(rule.keyword.toLowerCase())) {
                rule.boostCategories.forEach(catToBoost => {
                    if (categoryPriority[catToBoost]) { // Ensure category exists
                        categoryPriority[catToBoost] = (categoryPriority[catToBoost] || 1) * rule.factor;
                    }
                });
            }
        });
        saveCategoryStates(); // Save updated priorities
    }

    function generateMiniSummary() {
        const lang = currentLanguage;
        const summaryTemplates = {
            ar: {
                cognitive_passion: answer => `حتى الآن، فهمت أن لديك شغفًا بـ"${answer}". هل هذا دقيق؟`,
                ethical_values: answer => `يبدو أن قيمًا مثل "${answer.split(',')[0]}" مهمة لك. هل هذا صحيح؟`,
                project_objective: answer => `أرى أن لديك اهتمامًا بـ/هدفًا نحو "${answer.substring(0, 30)}...". هل تود التوسع؟`,
                general: () => `لقد شاركت بعض الأفكار المثيرة للاهتمام. هل تشعر أننا نسير في الاتجاه الصحيح لفهمك بشكل أفضل؟`
            },
            en: {
                cognitive_passion: answer => `So far, I understand you're passionate about "${answer}". Is that accurate?`,
                ethical_values: answer => `It seems values like "${answer.split(',')[0]}" are important to you. Is that right?`,
                project_objective: answer => `I see you have an interest in/goal towards "${answer.substring(0, 30)}...". Would you like to elaborate?`,
                general: () => `You've shared some interesting thoughts. Do you feel we're on the right track to understanding you better?`
            }
        };

        let summaryText = '';
        // Try to pick a recent, significant answer for a more specific summary
        const recentMeaningfulAnswers = Object.entries(userAnswers)
            .filter(([q, a]) => a && !a.startsWith('[') && a.length > 10) // Non-skipped, somewhat detailed
            .slice(-3); // Look at last 3 meaningful answers

        if (recentMeaningfulAnswers.length > 0) {
            const [lastQ, lastA] = recentMeaningfulAnswers[recentMeaningfulAnswers.length - 1];
            const categoryOfLastA = categorizeQuestionText(lastQ);
            if (summaryTemplates[lang][categoryOfLastA] && typeof summaryTemplates[lang][categoryOfLastA] === 'function') {
                summaryText = summaryTemplates[lang][categoryOfLastA](lastA);
            }
        }

        if (!summaryText) {
            summaryText = summaryTemplates[lang].general();
        }

        addMessage(summaryText, 'hypatia-message');
        lastAskedQuestionText = summaryText; // Treat summary as a question
        lastAskedQuestionCategory = 'summary_follow_up';
        followUpMode = true; // Expect a yes/no or short elaboration
    }

    function askFollowUpQuestion(answeredCategoryKey) {
        const lang = currentLanguage;
        const followUpQuestionTemplates = { /* Same as before, ensure keys match section keys */ };
        const followUpDetailsTemplates = { /* Same as before */ };
        const singleItemSections = [ /* Same as before */ ];

        // Retrieve actual follow-up questions from data.js if defined, or use generic ones.
        // This part needs to be carefully mapped to your data.js structure.
        // For now, we'll assume generic follow-ups if not a singleItemSection.

        if (singleItemSections.includes(answeredCategoryKey) || !sections[lang][answeredCategoryKey]) {
            currentQuestionIndex++; // Increment index for the completed/single-item section
            askQuestion();
            return;
        }

        // Example: Generic follow-up based on category
        const genericFollowUps = {
            ar: `هل هناك المزيد مما تود إضافته بخصوص "${sections[lang][answeredCategoryKey].title.replace('👤', '').trim()}"؟`,
            en: `Is there anything more you'd like to add regarding "${sections[lang][answeredCategoryKey].title.replace('👤', '').trim()}"?`
        };
        lastAskedQuestionText = genericFollowUps[lang] || genericFollowUps.en;
        lastAskedQuestionCategory = answeredCategoryKey + '_follow_up'; // Mark as follow-up for this category
        followUpMode = true;
        addMessage(lastAskedQuestionText, 'hypatia-message');
    }

    function getNextQuestionKeyAndIndex() {
        const langSections = sections[currentLanguage] || sections.en;
        const sectionKeys = Object.keys(langSections);

        const availableSections = sectionKeys.filter(key => {
            if (!langSections[key] || !langSections[key].questions) return false;
            const answeredCount = langSections[key].questions.filter(qText => userAnswers[qText] && !userAnswers[qText].startsWith('[')).length;
            return answeredCount < langSections[key].questions.length;
        });

        if (availableSections.length === 0) return null; // All sections completed

        availableSections.sort((keyA, keyB) => {
            const priorityA = categoryPriority[keyA] || 1;
            const priorityB = categoryPriority[keyB] || 1;
            // Factor in how long ago it was used and how many times, preferring less used/older ones with high priority
            const recencyFactorA = (totalAnswersGiven - (categoryUsage[keyA]?.lastUsedAtTotalAnswers || 0)) * 0.1;
            const recencyFactorB = (totalAnswersGiven - (categoryUsage[keyB]?.lastUsedAtTotalAnswers || 0)) * 0.1;
            const usageScoreA = (categoryUsage[keyA]?.count || 0) + recencyFactorA;
            const usageScoreB = (categoryUsage[keyB]?.count || 0) + recencyFactorB;

            // Higher score is better (higher priority, less recently/frequently used)
            const scoreA = priorityA / (usageScoreA + 1); // Add 1 to avoid division by zero
            const scoreB = priorityB / (usageScoreB + 1);
            return scoreB - scoreA; // Sort descending by score
        });

        const nextSectionKey = availableSections[0];
        const questionsInNextSection = langSections[nextSectionKey].questions;
        const nextQuestionIndexInSection = questionsInNextSection.findIndex(qText => !userAnswers[qText] || userAnswers[qText].startsWith('['));

        return { sectionKey: nextSectionKey, questionIndex: nextQuestionIndexInSection };
    }


    function askQuestion() {
        const nextQuestionInfo = getNextQuestionKeyAndIndex();

        if (!nextQuestionInfo) {
            if (!autoExported) {
                handleAutoExport(); // Changed function name
                autoExported = true;
            }
            addMessage(translations[currentLanguage].endOfQuestions, 'hypatia-message');
            generateNewQuestion();
            return;
        }

        currentSectionKey = nextQuestionInfo.sectionKey;
        currentQuestionIndex = nextQuestionInfo.questionIndex;

        const currentSectionData = sections[currentLanguage][currentSectionKey];
        const questionText = currentSectionData.questions[currentQuestionIndex];

        lastAskedQuestionText = questionText;
        lastAskedQuestionCategory = currentSectionKey; // The actual section key

        const sectionTitle = currentSectionData.title;
        const fieldType = currentSectionData.fieldType || 'text';
        const fieldOptions = currentSectionData.options || [];

        addMessage(questionText, 'hypatia-message', sectionTitle);
        setupDynamicInput(fieldType, fieldOptions); // Use the refined function

        // Update usage stats for the asked question's category
        categoryUsage[currentSectionKey].count = (categoryUsage[currentSectionKey].count || 0) + 1;
        categoryUsage[currentSectionKey].lastUsedAtTotalAnswers = totalAnswersGiven;
        saveCategoryStates();

        followUpMode = false; // Reset follow-up mode
    }

    function handleSendAnswer() {
        const answerText = getDynamicInputValue();
        if (!answerText) {
            showAlert(translations[currentLanguage].noAnswer, 'error');
            return;
        }

        toggleLoading(true);
        setTimeout(() => {
            addMessage(answerText, 'user-message');
            userAnswers[lastAskedQuestionText] = answerText; // Use the stored last asked question text as key
            localStorage.setItem('userAnswers', JSON.stringify(userAnswers));
            totalAnswersGiven++;

            updateCategoryPriorities(answerText, lastAskedQuestionCategory); // Update priorities based on the actual category of the question
            toggleLoading(false);

            const currentSectionData = sections[currentLanguage][lastAskedQuestionCategory]; // Use lastAskedQuestionCategory
            let isSectionComplete = false;
            if (currentSectionData && currentSectionData.questions) {
                 const answeredInSection = currentSectionData.questions.filter(q => userAnswers[q] && !userAnswers[q].startsWith('[')).length;
                 isSectionComplete = answeredInSection === currentSectionData.questions.length;
            }


            if (followUpMode) { // If it was a follow-up (e.g., from summary or category follow-up)
                followUpMode = false; // Reset follow-up mode
                if (isPositiveAnswer(answerText) && lastAskedQuestionCategory !== 'summary_follow_up') {
                    // If positive to a category follow-up, ask for more details (similar to old followUpDetails)
                    const detailPrompt = translations[currentLanguage].elaborationPrompt || // Define this in translations
                                         (currentLanguage === 'ar' ? `حسنًا، أخبرني المزيد عن ذلك.` : `Okay, tell me more about that.`);
                    addMessage(detailPrompt, 'hypatia-message');
                    lastAskedQuestionText = detailPrompt; // New "question"
                    lastAskedQuestionCategory = lastAskedQuestionCategory + '_elaboration'; // Mark as elaboration
                    // Don't set followUpMode again, let the next answer be a direct response
                } else {
                    // If negative, or summary follow-up, or no elaboration needed, move to next main question
                    currentQuestionIndex++; // This might need adjustment based on how sections are tracked
                    askQuestion();
                }
            } else { // Regular question answered
                recentCategories.push(lastAskedQuestionCategory);
                if (recentCategories.length > 4) recentCategories.shift(); // Keep last 4 non-follow-up categories

                if (isSectionComplete || totalAnswersGiven % 7 === 0) { // Trigger summary less frequently or on section completion
                    generateMiniSummary();
                } else {
                    askFollowUpQuestion(lastAskedQuestionCategory);
                }
            }
        }, 300); // Reduced timeout
    }

    function handleSkipQuestion() {
        if (!lastAskedQuestionText) return; // Nothing to skip

        userAnswers[lastAskedQuestionText] = `[${currentLanguage === 'ar' ? 'تم التخطي' : 'Skipped'}]`;
        localStorage.setItem('userAnswers', JSON.stringify(userAnswers));
        addMessage(`(${translations[currentLanguage].skip}: ${lastAskedQuestionText.substring(0,30)}...)`, 'user-message', null); // Show skip in chat

        // Adjust priority of the skipped question's category slightly downwards
        if (lastAskedQuestionCategory && categoryPriority[lastAskedQuestionCategory] > 0.5) {
            categoryPriority[lastAskedQuestionCategory] *= 0.9; // Reduce priority by 10%
            saveCategoryStates();
        }

        currentQuestionIndex++; // This needs to be handled carefully with dynamic section selection
        askQuestion();
    }

    function generateNewQuestion() {
        // This function needs significant refinement to be truly "smarter"
        // Current implementation is a placeholder based on previous logic
        toggleLoading(true);
        setTimeout(() => {
            const answers = Object.entries(userAnswers).filter(([_, a]) => a && !a.startsWith('['));
            if (answers.length < 5) { // Not enough data to generate a meaningful new question
                addMessage(translations[currentLanguage].notEnoughDataForNewQ || (currentLanguage === 'ar' ? "أحتاج المزيد من الإجابات لتوليد أسئلة جديدة مخصصة. لنواصل مع بعض الأسئلة الإضافية العامة." : "I need more answers to generate new custom questions. Let's continue with some general additional questions."), 'hypatia-message');
                // Ask a random question from a less used, high priority section if possible
                const nextFallback = getNextQuestionKeyAndIndex();
                if(nextFallback) {
                    askQuestion(); // It will pick based on priority
                } else {
                     addMessage(translations[currentLanguage].trulyEndOfQuestions || (currentLanguage === 'ar' ? "يبدو أننا استكشفنا كل شيء حاليًا!" : "It seems we've explored everything for now!"), 'hypatia-message');
                }
                toggleLoading(false);
                return;
            }

            // Simplified new question generation: Pick a less used category and ask its first unasked question
            // Or, pick a theme/keyword from answers and formulate a question.
            // For now, let's try to revisit a category that has high priority but was not fully explored, or a new one.

            let selectedWord = '';
            let targetCategoryKey = 'general';

            // Word frequency analysis (simple version)
            const stopWords = new Set(translations[currentLanguage].stopWords || (currentLanguage === 'ar' ? ['في', 'من', 'على', 'ما', 'هو', 'هل', 'أنا', 'أنت'] : ['the', 'a', 'is', 'i', 'you', 'what', 'my']));
            const wordCounts = {};
            answers.forEach(([q, a]) => {
                a.toLowerCase().split(/\s+/).forEach(word => {
                    if (word.length > 3 && !stopWords.has(word)) {
                        wordCounts[word] = (wordCounts[word] || 0) + 1;
                    }
                });
            });
            const sortedWords = Object.entries(wordCounts).sort((a, b) => b[1] - a[1]);
            if (sortedWords.length > 0) selectedWord = sortedWords[0][0];


            // Try to find a category related to the most frequent word, not recently asked
            const allSectionKeys = Object.keys(sections[currentLanguage]);
            let potentialCategories = allSectionKeys.filter(key =>
                !recentCategories.includes(key) &&
                (sections[currentLanguage][key].title.toLowerCase().includes(selectedWord) ||
                 sections[currentLanguage][key].questions.some(q => q.toLowerCase().includes(selectedWord)))
            );

            if (potentialCategories.length > 0) {
                potentialCategories.sort((a,b) => (categoryPriority[b] || 1) - (categoryPriority[a] || 1) );
                targetCategoryKey = potentialCategories[0];
            } else { // Fallback to a generally high-priority, less-used category
                 const sortedAllSections = allSectionKeys.filter(k => !recentCategories.includes(k) && sections[currentLanguage][k].questions.some(q => !userAnswers[q]));
                 if(sortedAllSections.length > 0) {
                    sortedAllSections.sort((a,b) => (categoryPriority[b] || 1) - (categoryPriority[a] || 1) );
                    targetCategoryKey = sortedAllSections[0];
                 }
            }


            let newQuestionText = '';
            if (targetCategoryKey !== 'general' && sections[currentLanguage][targetCategoryKey]) {
                const firstUnansweredInTarget = sections[currentLanguage][targetCategoryKey].questions.find(q => !userAnswers[q] || userAnswers[q].startsWith('['));
                if (firstUnansweredInTarget) {
                    newQuestionText = firstUnansweredInTarget;
                    lastAskedQuestionCategory = targetCategoryKey; // Set category for priority updates
                }
            }

            if (!newQuestionText) { // Ultimate fallback
                newQuestionText = selectedWord ?
                    (currentLanguage === 'ar' ? `بالحديث عن "${selectedWord}"، هل يمكنك توضيح المزيد حول هذا الموضوع؟` : `Speaking of "${selectedWord}", can you elaborate more on that topic?`) :
                    (translations[currentLanguage].genericNewQuestion || (currentLanguage === 'ar' ? "ما هو الشيء الذي تفكر فيه حاليًا؟" : "What's something on your mind right now?"));
                lastAskedQuestionCategory = 'generated_general';
            }

            lastAskedQuestionText = newQuestionText;
            addMessage(newQuestionText, 'hypatia-message', targetCategoryKey !== 'general' ? sections[currentLanguage][targetCategoryKey].title : '');
            setupDynamicInput('text', []); // Assume text input for generated questions

            if (targetCategoryKey !== 'general') {
                recentCategories.push(targetCategoryKey);
                if (recentCategories.length > 4) recentCategories.shift();
                categoryUsage[targetCategoryKey].count++;
                categoryUsage[targetCategoryKey].lastUsedAtTotalAnswers = totalAnswersGiven;
                saveCategoryStates();
            }
            toggleLoading(false);
        }, 500);
    }

    // --- DATA MANAGEMENT ---
    function handleAutoExport() {
        const dataStr = JSON.stringify({
            answers: userAnswers,
            usage: categoryUsage,
            priorities: categoryPriority,
            language: currentLanguage,
            totalAnswers: totalAnswersGiven,
            userId: userId,
            timestamp: new Date().toISOString()
        }, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `hypatia_protocol_${userId}_auto_${new Date().toISOString().slice(0,10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showAlert(translations[currentLanguage].exported);
    }

    function handleManualExport() {
        toggleLoading(true);
        setTimeout(() => {
            const exportData = {
                answers: userAnswers,
                usage: categoryUsage,
                priorities: categoryPriority,
                language: currentLanguage,
                totalAnswers: totalAnswersGiven,
                userId: userId,
                version: translations[currentLanguage].appVersion,
                timestamp: new Date().toISOString()
            };
            const dataStr = JSON.stringify(exportData, null, 2);
            const blob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `hypatia_protocol_${userId}_manual_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showAlert(translations[currentLanguage].exported);
            toggleLoading(false);
        }, 300);
    }

    function handleSaveProgress() {
        localStorage.setItem('userAnswers', JSON.stringify(userAnswers));
        saveCategoryStates(); // Also saves usage and priorities
        localStorage.setItem('hypatiaLanguage', currentLanguage);
        showAlert(translations[currentLanguage].saved);
    }

    function handleImportData(event) {
        const file = event.target.files[0];
        if (file) {
            toggleLoading(true);
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const importedFullData = JSON.parse(e.target.result);
                    let importedAnswers;

                    // Check for new comprehensive format vs old format (just answers)
                    if (importedFullData.answers && importedFullData.version) { // Likely new format
                        importedAnswers = importedFullData.answers;
                        if (importedFullData.usage) categoryUsage = { ...categoryUsage, ...importedFullData.usage };
                        if (importedFullData.priorities) categoryPriority = { ...categoryPriority, ...importedFullData.priorities };
                        if (importedFullData.language) currentLanguage = importedFullData.language;
                        if (importedFullData.totalAnswers) totalAnswersGiven = importedFullData.totalAnswers;
                         // Re-initialize states for any new categories from the current data.js not in imported file
                        initializeCategoryStates();
                    } else { // Assume old format (just an object of answers)
                        importedAnswers = importedFullData;
                        // For old format, we can't reliably restore usage/priorities, so user starts "fresh" with intelligence
                         Object.keys(sections[currentLanguage] || sections.en).forEach(key => {
                            categoryUsage[key] = { count: 0, lastUsedAtTotalAnswers: 0 };
                            categoryPriority[key] = 1;
                        });
                        totalAnswersGiven = Object.keys(importedAnswers).filter(q => importedAnswers[q] && !importedAnswers[q].startsWith('[')).length;
                    }


                    if (typeof importedAnswers !== 'object' || importedAnswers === null) {
                        throw new Error(translations[currentLanguage].invalidDataFormat);
                    }
                    const validatedAnswers = {};
                    for (const [q, a] of Object.entries(importedAnswers)) {
                        if (typeof q === 'string' && (typeof a === 'string' || a === null)) {
                            validatedAnswers[q] = a;
                        } else {
                             console.warn(`Invalid data entry during import: Q: ${q}, A: ${a}`);
                        }
                    }

                    userAnswers = { ...userAnswers, ...validatedAnswers }; // Merge, imported takes precedence

                    localStorage.setItem('userAnswers', JSON.stringify(userAnswers));
                    saveCategoryStates();
                    localStorage.setItem('hypatiaLanguage', currentLanguage);


                    updateInterfaceLanguage(); // Update based on potentially imported language
                    loadChatHistory(); // Reload chat with imported answers
                    showAlert(translations[currentLanguage].imported);
                    // Decide what to do next: ask a new question or let user resume
                    askQuestion(); // Ask next logical question based on imported state

                } catch (error) {
                    console.error("Import error:", error);
                    showAlert(`${translations[currentLanguage].importError} ${error.message}`, 'error');
                } finally {
                    toggleLoading(false);
                    importInput.value = null; // Reset file input
                }
            };
            reader.readAsText(file);
        }
    }

    function handleResetProtocol() {
        // Use generic modal for confirmation
        openModal(
            'resetConfirm', // Title key
            `<p>${translations[currentLanguage].resetConfirm}</p>`, // Body
            [
                { id: 'confirm-reset-btn', textKey: 'confirmButton', className: 'danger-button', onClick: () => {
                    localStorage.removeItem('userAnswers');
                    localStorage.removeItem('categoryUsage');
                    localStorage.removeItem('categoryPriority');
                    // localStorage.removeItem('hypatiaLanguage'); // Optionally keep language
                    localStorage.removeItem('hypatiaUserId'); // New user ID on reset

                    userAnswers = {};
                    categoryUsage = {};
                    categoryPriority = {};
                    totalAnswersGiven = 0;
                    recentCategories = [];
                    followUpMode = false;
                    autoExported = false;
                    currentSectionKey = null; // Reset current section
                    currentQuestionIndex = 0;
                     // Re-initialize user ID
                    const newUserId = 'user_' + Math.random().toString(36).substr(2, 9);
                    localStorage.setItem('hypatiaUserId', newUserId.split('_')[1]);
                    // No, userId is a const, cannot reassign. It should be a let if needs reset or use the one from LS.
                    // For now, we'll just clear it, next load will gen a new one.

                    initializeCategoryStates(); // Re-init priorities and usage for all sections
                    chatBox.innerHTML = ''; // Clear chat
                    showAlert(translations[currentLanguage].reset);
                    closeModal();
                    askQuestion(); // Start over
                }},
                { id: 'cancel-reset-btn', textKey: 'cancelButton', className: 'cancel-button', onClick: closeModal }
            ]
        );
    }

    // --- FEATURE MODALS ---
    function showEditAnswersModal() {
        const answeredQuestions = Object.entries(userAnswers)
            .filter(([_, answer]) => answer && !answer.startsWith('['));

        if (answeredQuestions.length === 0) {
            showAlert(translations[currentLanguage].noAnswers, 'error');
            return;
        }

        let body = `<label for="edit-question-select-modal">${translations[currentLanguage].editAnswers}:</label>
                    <select id="edit-question-select-modal" class="modal-input">`;
        answeredQuestions.forEach(([questionText]) => {
            body += `<option value="${escapeHTML(questionText)}">${escapeHTML(questionText.substring(0, 70))}${questionText.length > 70 ? '...' : ''}</option>`;
        });
        body += `</select>
                 <label for="edit-answer-textarea-modal">${translations[currentLanguage].newAnswerLabel || 'New Answer'}:</label>
                 <div id="edit-answer-input-area"></div>`; // Placeholder for dynamic input

        openModal(
            'editModalTitle',
            body,
            [
                { id: 'save-edit-btn', textKey: 'editModalSave', className: 'confirm-button', onClick: handleSaveEditedAnswer },
                { id: 'cancel-edit-btn', textKey: 'editModalCancel', className: 'cancel-button', onClick: closeModal }
            ]
        );

        const selectElement = document.getElementById('edit-question-select-modal');
        const answerInputArea = document.getElementById('edit-answer-input-area');

        function populateEditAnswerInput() {
            const selectedQuestionText = selectElement.value;
            const originalAnswer = userAnswers[selectedQuestionText] || '';
            let questionData = null;

            // Find the section and fieldType for the selected question
            for (const sectionKey in sections[currentLanguage]) {
                const section = sections[currentLanguage][sectionKey];
                if (section.questions.includes(selectedQuestionText)) {
                    questionData = { fieldType: section.fieldType, options: section.options || [] };
                    break;
                }
            }
            // Fallback for generated or old questions
            if (!questionData) questionData = { fieldType: 'text', options: []};


            answerInputArea.innerHTML = '';
            let editInputElement;

            if (questionData.fieldType === 'select') {
                editInputElement = document.createElement('select');
                editInputElement.className = 'modal-input';
                questionData.options.forEach(opt => {
                    const optionEl = document.createElement('option');
                    optionEl.value = opt;
                    optionEl.textContent = opt;
                    if (opt === originalAnswer) optionEl.selected = true;
                    editInputElement.appendChild(optionEl);
                });
            } else if (questionData.fieldType === 'checkbox') {
                editInputElement = document.createElement('div');
                editInputElement.className = 'checkbox-group modal-input';
                const currentAnswers = originalAnswer.split(',').map(s => s.trim());
                questionData.options.forEach(opt => {
                    const label = document.createElement('label');
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.value = opt;
                    if (currentAnswers.includes(opt)) checkbox.checked = true;
                    label.appendChild(checkbox);
                    label.appendChild(document.createTextNode(' ' + opt));
                    editInputElement.appendChild(label);
                });
            } else { // text
                editInputElement = document.createElement('textarea');
                editInputElement.className = 'modal-input';
                editInputElement.value = originalAnswer;
            }
            editInputElement.id = 'current-edit-answer-input'; // For retrieval
            answerInputArea.appendChild(editInputElement);
        }

        selectElement.addEventListener('change', populateEditAnswerInput);
        populateEditAnswerInput(); // Initial population
    }

    function handleSaveEditedAnswer() {
        const questionSelect = document.getElementById('edit-question-select-modal');
        const selectedQuestionText = questionSelect.value;
        const editInputElement = document.getElementById('current-edit-answer-input'); // The dynamic input itself
        let newAnswer;

        if(editInputElement.tagName === 'SELECT') {
            newAnswer = editInputElement.value;
        } else if (editInputElement.tagName === 'DIV') { // Checkbox group
            const checkedBoxes = editInputElement.querySelectorAll('input[type="checkbox"]:checked');
            newAnswer = Array.from(checkedBoxes).map(cb => cb.value).join(', ');
        } else { // Textarea
            newAnswer = editInputElement.value.trim();
        }


        if (newAnswer || newAnswer === '') { // Allow empty answer if user wants to clear it
            userAnswers[selectedQuestionText] = newAnswer;
            localStorage.setItem('userAnswers', JSON.stringify(userAnswers));
            showAlert(translations[currentLanguage].editSaved);
            loadChatHistory(); // Refresh chat
            closeModal();
        } else {
            // This case might not be hit if empty answer is allowed.
            // showAlert(translations[currentLanguage].noAnswer, 'error');
        }
    }

    function showSkippedQuestionsModal() {
        const skippedEntries = Object.entries(userAnswers)
            .filter(([_, answer]) => answer && answer.startsWith('[')); // [Skipped] or [تم التخطي]

        if (skippedEntries.length === 0) {
            showAlert(translations[currentLanguage].noSkipped);
            return;
        }

        let listHTML = `<p>${translations[currentLanguage].skippedList}</p><ul id="skipped-questions-list">`;
        skippedEntries.forEach(([questionText]) => {
            listHTML += `<li>
                            <span>${escapeHTML(questionText.substring(0,60))}${questionText.length > 60 ? '...' : ''}</span>
                            <a href="#" class="retry-link" data-question="${escapeHTML(questionText)}">${translations[currentLanguage].retrySkipped.split(' ')[0]}</a>
                         </li>`;
        });
        listHTML += `</ul>`;

        openModal(
            'skippedQuestionsTitle',
            listHTML,
            [{ id: 'close-skipped-btn', textKey: 'reportModalClose', className: 'cancel-button', onClick: closeModal }]
        );

        document.querySelectorAll('#skipped-questions-list .retry-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const questionToRetry = e.target.dataset.question;
                closeModal(); // Close this modal first

                // Set up to ask this question next
                lastAskedQuestionText = questionToRetry;
                lastAskedQuestionCategory = categorizeQuestionText(questionToRetry); // Determine its category
                delete userAnswers[questionToRetry]; // Remove "skipped" status
                localStorage.setItem('userAnswers', JSON.stringify(userAnswers));

                const sectionData = sections[currentLanguage][lastAskedQuestionCategory];
                let fieldType = 'text';
                let fieldOptions = [];
                if (sectionData) {
                    fieldType = sectionData.fieldType || 'text';
                    fieldOptions = sectionData.options || [];
                }
                
                addMessage(questionToRetry, 'hypatia-message', sectionData ? sectionData.title : '');
                setupDynamicInput(fieldType, fieldOptions);
                followUpMode = false; // It's a regular question now
            });
        });
    }

    function showReportModal() {
        let reportHTML = '';
        const langSections = sections[currentLanguage] || sections.en;

        Object.keys(langSections).forEach(sectionKey => {
            const sectionData = langSections[sectionKey];
            const sectionAnswers = sectionData.questions
                .map(qText => ({ question: qText, answer: userAnswers[qText] }))
                .filter(item => item.answer && !item.answer.startsWith('[')); // Answered and not skipped

            if (sectionAnswers.length > 0) {
                reportHTML += `<div class="report-section"><h5>${escapeHTML(sectionData.title)}</h5>`;
                sectionAnswers.forEach(item => {
                    reportHTML += `<p><strong>${escapeHTML(item.question)}:</strong> ${escapeHTML(item.answer)}</p>`;
                });
                reportHTML += `</div>`;
            }
        });
        // Add answers not fitting into current sections (e.g. generated, old lang)
        let otherAnswersHTML = '';
        Object.entries(userAnswers).forEach(([qText, answer]) => {
            if(answer && !answer.startsWith('[')) {
                let foundInSections = false;
                 for (const key in langSections) {
                    if(langSections[key].questions.includes(qText)) {
                        foundInSections = true;
                        break;
                    }
                }
                if(!foundInSections) {
                     if(otherAnswersHTML === '') otherAnswersHTML += `<div class="report-section"><h5>${translations[currentLanguage].otherAnswersTitle || (currentLanguage === 'ar' ? 'إجابات أخرى' : 'Other Answers')}</h5>`;
                     otherAnswersHTML += `<p><strong>${escapeHTML(qText)}:</strong> ${escapeHTML(answer)}</p>`;
                }
            }
        });
        if(otherAnswersHTML !== '') reportHTML += otherAnswersHTML + `</div>`;


        if (!reportHTML) {
            reportHTML = `<p>${translations[currentLanguage].noAnswers}</p>`;
        }
        openModal('reportTitle', reportHTML, [{id: 'close-report-btn', textKey: 'reportModalClose', className:'cancel-button', onClick: closeModal}]);
    }

    function showUserGuideModal() {
        openModal('userGuide', `<div id="guide-content">${translations[currentLanguage].userGuideText.replace(/\n/g, '<br>')}</div>`, [{id: 'close-guide-btn', textKey: 'guideModalClose', className:'cancel-button', onClick: closeModal}]);
    }

    function showLanguageModal() {
         let body = `<label for="language-select-modal">${translations[currentLanguage].languageModalTitle}:</label>
                    <select id="language-select-modal" class="modal-input">
                        <option value="ar" ${currentLanguage === 'ar' ? 'selected' : ''}>العربية</option>
                        <option value="en" ${currentLanguage === 'en' ? 'selected' : ''}>English</option>
                    </select>`;
        openModal(
            'languageModalTitle',
            body,
            [
                { id: 'save-lang-btn', textKey: 'languageModalSave', className: 'confirm-button', onClick: handleSaveLanguage },
                { id: 'cancel-lang-btn', textKey: 'languageModalCancel', className: 'cancel-button', onClick: closeModal }
            ]
        );
    }
    function handleSaveLanguage() {
        const langSelect = document.getElementById('language-select-modal');
        const newLanguage = langSelect.value;
        if (newLanguage !== currentLanguage) {
            currentLanguage = newLanguage;
            localStorage.setItem('hypatiaLanguage', currentLanguage);
            initializeCategoryStates(); // Re-check categories for the new language
            updateInterfaceLanguage();
            loadChatHistory(); // Reload chat in new language if possible
            // Potentially ask a new question or continue
            askQuestion(); // Ask next appropriate question
        }
        closeModal();
    }

    function escapeHTML(str) {
        if (typeof str !== 'string') return '';
        return str.replace(/[&<>"']/g, function (match) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            }[match];
        });
    }


    // --- EVENT LISTENERS ---
    menuButton.addEventListener('click', () => {
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', (e) => { // Close menu if clicked outside
        if (!menu.contains(e.target) && e.target !== menuButton && !menuButton.contains(e.target)) {
            menu.style.display = 'none';
        }
    });

    darkModeButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('hypatiaDarkMode', document.body.classList.contains('dark-mode'));
        updateDarkModeButtonText();
    });

    exportButton.addEventListener('click', handleManualExport);
    saveButton.addEventListener('click', handleSaveProgress);
    importButton.addEventListener('click', () => importInput.click());
    importInput.addEventListener('change', handleImportData);
    resetButton.addEventListener('click', handleResetProtocol);

    // Feature modal triggers
    editAnswersButton.addEventListener('click', showEditAnswersModal);
    skippedQuestionsButton.addEventListener('click', showSkippedQuestionsModal);
    reportButton.addEventListener('click', showReportModal);
    userGuideButton.addEventListener('click', showUserGuideModal);
    languageButton.addEventListener('click', showLanguageModal);

    // --- START THE APP ---
    initializeApp();
});