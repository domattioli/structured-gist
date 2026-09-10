- **Compute-farm update**
  - A. ~12 new Sun Blade-100s ordered
  - B. `run-command` finds fastest free machine
  - C. machine attributes target OS/speed/no-evict
  - D. self-limit ~10 jobs; P-make `-J` caps concurrency

- **Aurora enhancement progress**
  - A. new clean-speech-trained LDA filters, slight gain
  - B. on-line normalization needs retuned time constant
  - C. endpoints alone: +22% baseline, +50% on Spanish
  - D. now prototyping signal-subspace enhancement in Matlab

- **Proposal-one vs France Telecom**
  - A. France-Telecom spectral subtraction + proposal-one improves significantly
  - B. beats France Telecom on mismatch/high-mismatch, slightly worse well-matched
  - C. well-matched = 70/30 split, not guaranteed matched

- **Enhancement combination ideas**
  - A. spectral subtraction: mel energies vs FFT bins, unclear winner
  - B. two-stage enhancement common elsewhere, worth trying
  - C. signal subspace = KL transform + built-in Wiener filter
  - D. VTS approach pursued at Grenada + Lucent, originally CMU

- **WSJ large-vocabulary plans**
  - A. next stage: noisy large-vocabulary WSJ task
  - B. literature favors Wiener/subspace over spectral subtraction at scale
  - C. Hari's visit to help pick shared direction

- **New voicing feature**
  - A. variance-of-spectral-difference feature for voicing
  - B. needs longer ~62.5ms analysis window
  - C. no significant gain over plain cepstrum

- **Discarded-information question**
  - A. irreversible transforms drop information — what got lost?
  - B. proposal: feed raw FFT spectrum into a neural net directly
  - C. binary speech/silence bit already helped noisy SpeechDat-Car, esp. Italian

- **Acoustic-event project**
  - A. qualifier project: detect events (voicing, nasality, frication...)
  - B. tandem-style into GMM-HMM back end
  - C. open: which events, how to get labels

- **Formant-tracking work**
  - A. roots PLP/LPC polynomial to find spectral peaks
  - B. psycho-acoustic proxy, not the synthesizer's true formants
