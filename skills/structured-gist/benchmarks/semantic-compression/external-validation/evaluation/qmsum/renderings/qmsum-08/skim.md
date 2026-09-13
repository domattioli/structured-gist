- **Agenda-request process**
  - A. Andreas wants topics known in advance so he can skip irrelevant meetings
  - B. Adam volunteers to send a Tue/Wed reminder for agenda items

- **Mic and channel expansion**
  - A. two new mics arriving, being assembled
  - B. considering more comfortable wireless headsets
  - C. proposing a second wireless base station (~$900 + $800/channel) to replace remaining wired mikes
  - D. Sony radio mikes reliable so far if batteries are managed

- **Digits status**
  - A. paperwork now digitized with scripts for transcriber tools
  - B. Dave Gelbart will be first user once digits are ready
  - C. Dave absent — signal-processing class conflict

- **Transcription and corpus status**
  - A. ~35 hours recorded so far, most non-digit
  - B. ~11 hours transcribed; cleaning pass covers spelling, markup, numbers/acronyms, VOC/NONVOC/GLOSS tags
  - C. next: channelize data, tighten segment boundaries
  - D. spot-check: two transcribers nearly identical, differing mainly on technical vs colloquial vocabulary

- **Channel-based speech detector (Adam)**
  - A. ran per-channel HMM speech/nonspeech detector in new multichannel format
  - B. switched to loudness-based (not log-domain) features
  - C. normalized loudness within-channel to separate foreground/background speech

- **Bleep-editing system design**
  - A. Adam's plan: password-gated web pages, checkbox bleeps submitted by email
  - B. Morgan worried convenience will cause over-bleeping and fragment the corpus
  - C. resolved: email first for simple approval; web/password access only if someone wants to review further
  - D. bleeps applied only at release time, whole utterances only, email approval treated as sufficient consent
