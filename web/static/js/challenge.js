class ChallengeModal {
  constructor(container, onSubmit) {
    this.container = container;
    this.onSubmit = onSubmit;
    this.questionEl = document.getElementById('challenge-question');
    this.optionsEl = document.getElementById('challenge-options');
    this.inputEl = document.getElementById('challenge-input');
    this.feedbackEl = null;
    this.buttons = [];
  }

  show(challenge) {
    this.container.classList.remove('hidden');
    this.questionEl.textContent = challenge.question;
    this.optionsEl.innerHTML = '';
    this.inputEl.value = '';
    this.buttons = [];

    if (challenge.type === 'multiple_choice' && challenge.options) {
      this._renderMultipleChoice(challenge);
    } else {
      this._renderTextChallenge(challenge);
    }
  }

  setInputEnabled(enabled) {
    // Disable buttons during submission
    this.buttons.forEach(btn => {
      btn.disabled = !enabled;
      btn.style.opacity = enabled ? 1 : 0.5;
    });
    if (this.inputEl) {
      this.inputEl.disabled = !enabled;
    }
  }

  showFeedback(isCorrect) {
    this.questionEl.style.color = isCorrect ? '#00ff00' : '#ff4444';
    this.questionEl.textContent = isCorrect ? 'CORRECT!' : 'WRONG!';
    this.questionEl.style.fontSize = '36px';
  }

  _renderMultipleChoice(challenge) {
    const options = challenge.options || [];
    this.buttons = [];
    options.forEach((opt, i) => {
      const btn = document.createElement('button');
      btn.className = 'challenge-option-btn';
      btn.textContent = `${i + 1}. ${opt}`;
      btn.addEventListener('click', () => this.onSubmit(opt));
      this.optionsEl.appendChild(btn);
      this.buttons.push(btn);
    });

    // Keyboard shortcuts 1/2/3
    this._keyHandler = (e) => {
      const num = parseInt(e.key);
      if (num >= 1 && num <= options.length) {
        this.onSubmit(options[num - 1]);
      }
    };
    document.addEventListener('keydown', this._keyHandler);
  }

  _renderTextChallenge(challenge) {
    this.inputEl.classList.remove('hidden');
    this.inputEl.focus();

    const submitHandler = () => {
      this.onSubmit(this.inputEl.value);
    };

    this.inputEl.onkeydown = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        submitHandler();
      }
    };

    // Store handler for cleanup
    this._submitHandler = submitHandler;
  }

  hide() {
    this.container.classList.add('hidden');
    this.optionsEl.innerHTML = '';
    this.inputEl.value = '';
    this.inputEl.classList.add('hidden');

    // Reset styling
    this.questionEl.style.color = '';
    this.questionEl.style.fontSize = '';

    if (this._keyHandler) {
      document.removeEventListener('keydown', this._keyHandler);
      this._keyHandler = null;
    }
    if (this._submitHandler) {
      this.inputEl.onkeydown = null;
      this._submitHandler = null;
    }
  }
}
