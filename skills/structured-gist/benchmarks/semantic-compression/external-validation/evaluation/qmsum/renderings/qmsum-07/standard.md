- **Session setup**
  - **Mic switch**
    - group dropped lapel mics for wireless headsets; lapels sat in a noisy middle ground — not distant enough to be representative far-field mics, not close enough to avoid interference
  - **Session ID**
    - recording is session R-19; new arrival Sunil is present for the summer

- **Compute-farm update**
  - **New hardware**
    - about a dozen Sun Blade-100s ordered to build out a shared compute farm
  - **Job dispatch (`run-command`)**
    - i. finds the fastest currently available machine and exports the job to it, duplicating the caller's environment
    - ii. supports attributes (OS, speed, memory, machine name, "no-evict") to target where a job runs
    - iii. jobs can get evicted if a non-"no-evict" desktop machine's owner returns and starts typing — the job auto-restarts elsewhere, costing time
  - **Parallel-job etiquette**
    - a. run-command doesn't coordinate across jobs, so users should self-limit to roughly ten simultaneous jobs to avoid saturating shared machines
    - b. P-make tracks the whole job set and enforces a hard concurrency cap via `-J <N>`, removing the need for manual throttling logic

- **Aurora enhancement progress (Sunil)**
  - **LDA redesign**
    - new filters trained on clean speech (rather than the narrow-band filters originally submitted) gave a slight, not major, improvement — appropriate since enhancement already cleans the signal before LDA runs
  - **On-line normalization**
    - the submitted mean/variance update time constant doesn't suit enhanced speech; without retuning it, on-line normalization gave no improvement over skipping it
  - **Endpoint information**
    - I. supplying speech/nonspeech endpoints to the plain Aurora baseline (no enhancement) improved it by 22% overall
    - II. on one SpeechDat-Car set (Spanish) endpoints alone gave a 50% improvement, large enough that the qualification bar was cut from 50% to about 25% for well-matched
  - **Signal-subspace approach**
    - decomposes noisy signal into signal/noise subspaces to estimate clean speech; currently prototyped in Matlab, to be ported to C and checked into the shared repository once it shows a positive result

- **Proposal-one vs France Telecom (Dave/PhD D)**
  - **Setup**
    - took France Telecom's handset-side spectral subtraction output (already Wiener-filtered before cepstral conversion) and ran the full proposal-one system on top, with a modification to reduce LDA filter delay
  - **Result**
    - plugging in spectral subtraction improved results significantly, but only after retuning the on-line normalization time constants — the submitted value did nothing either way
  - **Comparison to France Telecom**
    - i. new system is consistently better on mismatch and high-mismatch conditions
    - ii. slightly (not significantly) worse on well-matched, though it still reads worse on a results spreadheet
    - iii. expected to matter less once frame dropping is added to the baseline, which should lift HM/MM scores broadly and even out each contribution
  - **What "well-matched" means**
    - defined as a 70/30 train/test split of the same database, not a guaranteed match like TI-digits' artificial noise — natural recordings can still carry mismatch from noise levels and silence-frame content

- **Combining enhancement techniques**
  - **Spectral-subtraction domain**
    - can run on mel energies or on FFT bins; both are used across submissions and neither is clearly better for recognition, since a linear weighting follows either way
  - **Two-stage enhancement**
    - most Aurora submissions run their enhancement twice and see a real gain; worth trying for the signal-subspace approach too, and worth testing which technique should run first
  - **Signal subspace = KL transform + Wiener filter**
    - the approach already embeds a Wiener filter (KL transform then Wiener filter), but performs poorly at low SNR and with colored noise because it depends on inverting a noise covariance matrix that must be positive definite (true for white noise, not colored) — colored noise is worked around by inverse-filtering to whiten it first, then re-filtering after reconstruction
  - **Vector Taylor Series (VTS)**
    - a first/second-order Taylor approximation of the nonlinear clean/noisy-cepstra transformation, used to remove noise and channel effects; pursued by Jose Carlos Segura's group in Grenada and a contact at Lucent, tracing back to CMU

- **WSJ / large-vocabulary plans**
  - **Next stage**
    - the group will soon tackle Wall Street Journal with artificially added noise (parallel to what was done with TI-digits), likely coordinated by Guenter Hirsch and TI
  - **Literature caveat**
    - most published speech-enhancement results are on small-vocabulary tasks; what little exists suggests spectral subtraction underperforms Wiener filtering and subspace methods at large vocabulary, so simple spectral subtraction may need extra optimization
  - **Prior large-vocab noisy-speech experience**
    - the group's Broadcast News evaluation handled noisy large-vocabulary speech with multi-stream techniques (not spectral subtraction) and it helped; current meeting-recording data adds noisy/reverberant far-field audio, now also run through a Switchboard-trained recognizer with some adaptation, though no one has yet tried the distant mike with the SRI recognizer
  - **Coordination**
    - Hari's visit in a week or two is meant to help settle on a shared game plan — either converge everyone on one promising direction, or run two plausible approaches in parallel until one wins out

- **New voicing feature (PhD B)**
  - **Feature definition**
    - reconstructs an approximate signal spectrum from the mel-filterbank output, compares it against the true FFT spectrum, and uses the variance of that difference as a voiced/unvoiced discriminator (high variance ~ noise, low variance ~ speech)
  - **Preprocessing change**
    - required lengthening the analysis window to about 62.5ms to get enough information for the feature
  - **Experiments**
    - a. fed directly alongside cepstral features
    - b. fed into a small neural net trained to classify voiced/unvoiced/silence
    - c. tested on Italian and Spanish
  - **Result**
    - neural-net version was roughly on par with (sometimes slightly worse, sometimes slightly better than) cepstrum-only; feeding the raw feature directly performed worse than the neural-net route

- **Discarded-information discussion (Professor C)**
  - **Framing**
    - any irreversible feature condensation throws information away on purpose, to suppress unwanted variability — but it's worth checking whether something useful also got discarded
  - **Proposal**
    - feed the raw FFT power spectrum into a neural net the same way the filterbank is used, alone or combined, to let the network find whatever the filterbank is missing
  - **Skepticism and precedent**
    - i. PhD D notes the raw power spectrum carries a lot of variability
    - ii. Professor C recalls a ~10-year-old conference where a simple FFT front-end beat an auditory-inspired one at a neighboring poster — variability is real, but statistical models can often handle it
    - iii. same trade-off shows up with data-driven LDA filters: data-driven methods can capture more but also risk mismatch between training and test data
  - **Existing precedent that worked**
    - adding a binary speech/nonspeech bit to the cepstrum, trained into the HMM, gave a large improvement on noisy SpeechDat-Car (especially Italian) but little on TI-digits, where there was less to discriminate
  - **Related literature**
    - an ICASSP paper extracted higher-order cepstral moments/cumulants for a small gain on noisy small-vocabulary speech; Professor C argues a neural net implicitly computes something similar, just less explicitly

- **Acoustic-event project (Grad G, qualifier work)**
  - **Goal**
    - build robust primary detectors for acoustic events (voicing, nasality, R-coloring, burst/noise, frication, etc.), inspired by multi-band techniques and Larry Saul's graphical-models work, then feed detector outputs tandem-style into a GMM-HMM back end
  - **Open questions**
    - i. which set of acoustic events gives adequate coverage for downstream recognition
    - ii. how to obtain labeled training data for those events
  - **Connection noted**
    - Professor C points out the voiced/unvoiced piece overlaps directly with PhD B's variance-difference feature and the multi-band approach that seems to help there
  - **Recent work**
    - has started exploring TRAPS applied to these same acoustic events

- **Formant/peak-tracking work (Grad E)**
  - **Context**
    - helping outside researcher Pierre Divenyi study perception of formant transitions using synthetic vowel-to-vowel audio, comparing a psycho-acoustic spectrum's energy movement to listener test results
  - **Method**
    - finds the roots of the PLP-derived LPC polynomial (an approach similar to line spectral pairs) to track spectral peaks over time; complex-conjugate root pairs are treated like second-order IIR sections, potentially also yielding bandwidth estimates
  - **Caveat**
    - the tracked peaks are a psycho-acoustic proxy shaped by the PLP model, not the synthesizer's actual formant values, though the true formants could be pulled directly from the synthesizer instead

- **Housing note**
  - Sunil is still looking for a place; a room may open May 30th, and a labmate offered a spare bedroom as backup; he plans to return the 31st regardless

- **Digits wrap-up**
  - meeting closes with the usual end-of-session digit reading for the corpus
