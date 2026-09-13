- **Session admin**
  - session logged as MR-11, correcting an earlier "R-9" label; no front-end meeting happened that day

- **Audio-spike question**
  - Jane noticed spikes/clicks in some recorded channels, including her own; Adam suspects touching/fiddling or a bad connector on a wired mike rather than an electronics problem, so it's dropped from further discussion

- **Agenda-request process**
  - **Motivation**
    - Andreas, peripherally involved, wants to know discussion topics in advance so he can skip meetings that don't concern him and save everyone's time — meetings have grown large when everyone attends
  - **Plan**
    - i. Adam volunteers to send a reminder (Tuesday or Wednesday) asking people to submit agenda items ahead of the meeting
    - ii. Professor E is skeptical it'll work well (the admin meeting's agenda requests usually arrive ten minutes before), but agrees it's worth trying
  - **Refinement**
    - Jane suggests Andreas specify particular topics of interest so the group can more precisely flag relevant meetings for him

- **Mic and channel expansion**
  - **New hardware**
    - two new mics have arrived and are being assembled; group currently has five working wireless channels (one base station, six possible receivers) with one more coming
  - **Headset comfort**
    - if the other available headsets prove more comfortable, the group should switch, pending evaluation once they arrive
  - **Second wireless base station**
    - i. daisy-chaining base stations would allow replacing the remaining wired mikes (2 working, 1 broken) with wireless, since wireless has proven more reliable
    - ii. cost: ~$900 for a base station plus ~$800 per additional channel; Professor E approves immediately given the low marginal cost
  - **Comparison to other sites**
    - UW is close to buying an off-the-shelf setup; SRI is separately evaluating options; group agrees to compare notes with both, while avoiding discussion of funding specifics on the record
  - **Reliability**
    - Sony radio mikes have been reliable as long as batteries are monitored; wired mikes and the "Jimbox" path have caused more problems
  - **Headset connector repair**
    - the headset connector change involves hand-soldering, but it's being done by the vendor's repair shop, not in-house

- **Digits status**
  - **Digitized paperwork**
    - Adam converted all digit forms to computer records and wrote scripts so transcribers can use different tools, plus scripts to generate P-files and run recognition
  - **Transition**
    - Jane, per an earlier decision that transcribers shouldn't handle paperwork, is meeting with Dave today to move to using Adam's interface
  - **First user**
    - Dave Gelbart is expected to be the first user of the digits once ready (five or six sets already done); he's absent today due to a signal-processing class (225A) conflict, and isn't reliably on the meeting invite list — Adam will fix that

- **Transcription and corpus status**
  - **Volume**
    - roughly 35 hours recorded total (including digits, not yet separated out) — comfortably more than 30 hours of non-digit content, since digits take under half a minute per person; about 11 hours transcribed so far out of a 12-hour batch given to transcribers, with two transcribers still finishing it
  - **Cleaning pass (Jane's top priority)**
    - i. spell-checking and consistent markup throughout
    - ii. new conventions from Liz: systematic handling of numbers (e.g. distinguishing "nine two" vs "ninety-two" with a gloss) and acronyms (letters space-separated, e.g. "P Z M", possibly glossed)
    - iii. explicit comment-type tags — `VOC` (vocalized, e.g. cough/laugh), `NONVOC` (e.g. door slam), `GLOSS` (pronunciation/spoken-form notes) — applied via an automated filter rather than by hand, to reduce transcriber error; PhD B separately suggests alphabetized word-frequency listings to catch misspellings, which Jane already uses
  - **Spot-check**
    - compared two transcribers' independent output on the same 10-minute segment: nearly word-for-word identical (differences mainly in optional comma placement); each had different vocabulary blind spots — one caught "neural nets," the other caught "gobbledy-gook" (the first approximated it phonetically as unsure)
  - **Next steps**
    - after cleaning, data gets "channelized" into multichannel format for Liz and Don to use, then Jane will tighten the boundaries of segment time bins; Thilo had a breakthrough on channel-based speech/nonspeech segmentation that Jane hasn't yet had time to apply

- **Channel-based speech/nonspeech detector (Adam)**
  - **What changed**
    - ran the same underlying HMM-based detector, now per-channel in the new multichannel format, and gave one processed meeting to Liz to test with the recognizer, which had been running into memory problems on long unsegmented speech chunks
  - **Feature changes**
    - switched from log-domain loudness features to a different loudness-based scaling (a named psychoacoustic curve Adam couldn't recall, possibly Fletcher-Munson-related) and normalized loudness/modified-loudness within each channel
  - **Cross-channel knowledge**
    - the only cross-channel step so far is energy normalization across all channels; the within-channel normalization helps distinguish foreground from background speech, working well but not always

- **Bleep-editing system design (main debate)**
  - **Adam's proposed system**
    - generates password-protected web pages per meeting (one password per person, restricted to meeting participants) showing transcript utterances with checkboxes; submitting the form emails Adam the time intervals to exclude — chosen to avoid distributing raw transcript text over insecure email
  - **Morgan's concern**
    - i. worries the elaborate web workflow over-serves a rare case — most participants will just say "it's fine" — and prefers a simpler default: contact people first (e.g. print a transcript, ask if it's OK), reserving the web/password mechanism for the rarer person who wants to review closely
    - ii. worries that making bleeping too easy/fun will lead people to remove more than necessary, degrading the corpus for future researchers who need complete dialogue; PhD B frames it as "the easier it is, the more gets bleeped"
  - **Adam's counterpoints**
    - the web form was mainly for his own convenience (structured, emailed, ready to insert); most people will just reply "OK" via email, which is easy either way; a printable version can still be offered for those who want it
  - **Points of dispute resolved**
    - i. participants may bleep sections even where they weren't speaking themselves, if they feel a conversation partner's remarks make their own identity inferable — Jane and Adam argue the consent form supports this broader right, over PhD B's discomfort with one person editing another's words
    - ii. no physical signature is required; email approval is sufficient, since participants already signed a consent form permitting this review step
    - iii. bleeping happens only at whole-utterance granularity (not sub-utterance), purely for Adam's convenience in editing transcript files
    - iv. bleeps are applied to the data only at release time (kept as a list of time intervals until then), to avoid maintaining duplicate copies under tight disk space
  - **Final compromise**
    - a. first, email each participant asking for a simple approval, worded to bias toward keeping full data (framing full-corpus use as valuable to the field) without misrepresenting anything
    - b. only issue a web password if someone specifically wants to review further; passwords are distributed by phone, in person, or physical mail — never by email, for security
    - c. Jane notes the consent form already promises access to the transcript (not necessarily proactive delivery), and raises a legal concern that making review too hard could shift liability back onto the group if something objectionable slips through
    - d. group agrees corrections (participants disputing what the transcript says they said) would also be valuable feedback to collect

- **Wrap-up**
  - Grad D has nothing specific to report this week; meeting closes with a digits-reading session, having found more unfilled digit forms than expected
