class ChallengeModal {
  constructor(container, onSubmit) {
    // Feedback duration: 750ms
    this.container = container;
    this.onSubmit = onSubmit;
    this.questionEl = document.getElementById('challenge-question');
    this.optionsEl = document.getElementById('challenge-options');
    this.inputEl = document.getElementById('challenge-input');
    this.feedbackEl = null;
  }

  show(challenge) {
    this.container.classList.remove('hidden');
    this.questionEl.textContent = challenge.question;
    this.optionsEl.innerHTML = '';
    this.inputEl.value = '';

    if (challenge.type === 'multiple_choice' && challenge.options) {
      this._renderMultipleChoice(challenge);
    } else {
      this._renderTextChallenge(challenge);
    }
  }

  hide() {
    this.container.classList.add('hidden');
    this.optionsEl.innerHTML = '';
    this.inputEl.value = '';
  }

  _renderMultipleChoice(challenge) {
    const options = challenge.options || [];
    options.forEach((opt, i) => {
      const btn = document.createElement('button');
      btn.className = 'challenge-option-btn';
      btn.textContent = `${i + 1}. ${opt}`;
      btn.addEventListener('click', () => this.onSubmit(opt));
      this.optionsEl.appendChild(btn);
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
