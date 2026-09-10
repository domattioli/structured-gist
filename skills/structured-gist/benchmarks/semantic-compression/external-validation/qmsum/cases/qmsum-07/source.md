# QMSum meeting transcript — Academic — Bro019

<!-- source: Yale-LILY/QMSum, commit 83d7768c1f2b4dfeb091385d3dc7e239b8e5bb7e, MIT license -->

**Professor C:** Uh , is it the twenty - fourth ?

**PhD F:** now we 're on .

**Professor C:** Yeah .

**PhD A:** Uh Chuck , is the mike type wireless {disfmarker}

**PhD F:** Yes .

**PhD A:** wireless headset ? OK .

**PhD F:** Yes .

**Professor C:** Yeah .

**PhD F:** For you it is .

**Professor C:** Yeah . We uh {disfmarker} we abandoned the lapel because they sort of were not too {disfmarker} not too hot , not too cold , they were {disfmarker} you know , they were {vocalsound} uh , far enough away that you got more background noise , uh , and uh {disfmarker} and so forth

**PhD A:** Uh - huh .

**Professor C:** but they weren't so close that they got quite the {disfmarker} you know , the really good {disfmarker} No , th

**PhD A:** OK .

**Professor C:** they {disfmarker} I mean they didn't {disfmarker} Wait a minute . I 'm saying that wrong . They were not so far away that they were really good representative distant mikes ,

**PhD A:** Uh - huh .

**Professor C:** but on the other hand they were not so close that they got rid of all the interference . So it was no {disfmarker} didn't seem to be a good point to them . On the other hand if you only had to have one mike in some ways you could argue the lapel was a good choice , precisely because it 's in the middle .

**PhD A:** Yeah , yeah .

**Professor C:** There 's uh , some kinds of junk that you get with these things that you don't get with the lapel uh , little mouth clicks and breaths and so forth are worse with these than with the lapel , but given the choice we {disfmarker} there seemed to be very strong opinions for uh , getting rid of lapels .

**PhD A:** The mike number is {disfmarker}

**Professor C:** So ,

**PhD F:** Uh , your mike number 's written on the back of that unit there .

**PhD A:** Oh yeah . One .

**PhD F:** And then the channel number 's usually one less than that .

**PhD A:** Oh , OK . OK .

**PhD F:** It - it 's one less than what 's written on the back of your {disfmarker}

**PhD A:** OK . OK .

**PhD F:** yeah . So you should be zero , actually .

**PhD A:** Hello ? Yeah .

**PhD F:** For your uh , channel number .

**PhD A:** Yep , yep .

**Professor C:** And you should do a lot of talking so we get a lot more of your pronunciations . no , they don't {disfmarker} don't have a {disfmarker} have any Indian pronunciations .

**PhD F:** So what we usually do is um , we typically will have our meetings

**Professor C:** Yeah .

**PhD F:** and then at the end of the meetings we 'll read the digits . Everybody goes around and reads the digits on the {disfmarker} the bottom of their forms .

**Professor C:** Session R

**PhD D:** R - nineteen ?

**PhD A:** OK .

**Professor C:** R - nineteen .

**PhD F:** Yeah . We 're {disfmarker} This is session R - nineteen .

**Professor C:** If you say so . O K . Do we have anything like an agenda ? What 's going on ? Um . I guess um . So . One thing {disfmarker}

**PhD F:** Sunil 's here for the summer ?

**Professor C:** Sunil 's here for the summer , right . Um , so , one thing is to talk about a kick off meeting maybe uh , and then just uh , I guess uh , progress reports individually , and then uh , plans for where we go between now and then , pretty much . Um .

**PhD F:** I could say a few words about um , some of the uh , compute stuff that 's happening around here , so that people in the group know .

**Professor C:** Mm - hmm . OK . Why don't you start with that ? That 's sort of {disfmarker}

**PhD F:** OK .

**Professor C:** Yeah ?

**PhD F:** We um {disfmarker} So we just put in an order for about twelve new machines , uh , to use as sort of a compute farm . And um , uh , we ordered uh , SUN - Blade - one - hundreds , and um , I 'm not sure exactly how long it 'll take for those to come in , but , uh , in addition , we 're running {disfmarker} So the plan for using these is , uh , we 're running P - make and Customs here and Andreas has sort of gotten that all uh , fixed up and up to speed . And he 's got a number of little utilities that make it very easy to um , {vocalsound} run things using P - make and Customs . You don't actually have to write P - make scripts and things like that . The simplest thing {disfmarker} And I can send an email around or , maybe I should do an FAQ on the web site about it or something . Um ,

**Professor C:** How about an email that points to the FAQ ,

**PhD F:** there 's a c

**Professor C:** you know what I 'm saying ?

**PhD F:** Yeah , yeah .

**Professor C:** so that you can {disfmarker} Yeah .

**PhD F:** Uh , there 's a command , uh , that you can use called " run command " . " Run dash command " , " run hyphen command " . And , if you say that and then some job that you want to execute , uh , it will find the fastest currently available machine , and export your job to that machine , and uh {disfmarker} and run it there and it 'll duplicate your environment . So you can try this as a simple test with uh , the L S command . So you can say " run dash command L S " , and , um , it 'll actually export that {vocalsound} LS command to some machine in the institute , and um , do an LS on your current directory . So , substitute LS for whatever command you want to run , and um {disfmarker} And that 's a simple way to get started using {disfmarker} using this . And , so , soon , when we get all the new machines up , {vocalsound} um , e then we 'll have lots more compute to use . Now th one of the nice things is that uh , each machine that 's part of the P - make and Customs network has attributes associated with it . Uh , attributes like how much memory the machine has , what its speed is , what its operating system , and when you use something like " run command " , you can specify those attributes for your program . For example if you only want your thing to run under Linux , you can give it the Linux attribute , and then it will find the fastest available Linux machine and run it on that . So . You can control where your jobs go , to a certain extent , all the way down to an individual machine . Each machine has an attribute which is the name of itself . So you can give that as an attribute and it 'll only run on that . If there 's already a job running , on some machine that you 're trying to select , your job will get queued up , and then when that resource , that machine becomes available , your job will get exported there . So , there 's a lot of nice features to it and it kinda helps to balance the load of the machines and uh , right now Andreas and I have been the main ones using it and we 're {disfmarker} Uh . The SRI recognizer has all this P - make customs stuff built into it .

**Professor C:** So as I understand , you know , he 's using all the machines and you 're using all the machines ,

**PhD F:** So .

**Professor C:** is the rough division of {disfmarker}

**PhD F:** Yeah . Exactly . Yeah , you know , I {disfmarker} I sort of got started {comment} using the recognizer just recently and uh , uh I fired off a training job , and then I fired off a recognition job and I get this email about midnight from Andreas saying , " uh , are you running two {vocalsound} trainings simultaneously s my m my jobs are not getting run . " So I had to back off a little bit . But , soon as we get some more machines then uh {disfmarker} then we 'll have more compute available . So , um , that 's just a quick update about what we 've got . So .

**Grad G:** Um , I have {disfmarker} I have a question about the uh , parallelization ?

**PhD F:** Mm - hmm .

**Grad G:** So , um , let 's say I have like , a thousand little {disfmarker} little jobs to do ?

**PhD F:** Mm - hmm .

**Grad G:** Um , how do I do it with " run command " ? I mean do {disfmarker}

**PhD F:** You could write a script uh , which called run command on each sub - job

**Grad G:** Uh - huh . A thousand times ?

**PhD F:** right ? But you probably wanna be careful with that

**Grad G:** OK .

**PhD F:** because um , you don't wanna saturate the network . Uh , so , um , you know , you should {disfmarker} you should probably not run more than , say ten jobs yourself at any one time , uh , just because then it would keep other people {disfmarker}

**Grad G:** Oh , too much file transfer and stuff .

**PhD F:** Well it 's not that so much as that , you know , e with {disfmarker} if everybody ran fifty jobs at once then it would just bring everything to a halt and , you know , people 's jobs would get delayed , so it 's sort of a sharing thing . Um ,

**Grad G:** OK .

**PhD F:** so you should try to limit it to somet sometim some number around ten jobs at a time . Um . So if you had a script for example that had a thousand things it needed to run , um , you 'd somehow need to put some logic in there if you were gonna use " run command " , uh , to only have ten of those going at a time . And uh , then , when one of those finished you 'd fire off another one . Um ,

**Professor C:** I remember I {disfmarker} I forget whether it was when the Rutgers or {disfmarker} or Hopkins workshop , I remember one of the workshops I was at there were {disfmarker} everybody was real excited cuz they got twenty - five machines and there was some kind of P - make like thing that sit sent things out .

**PhD F:** Mm - hmm . Mm - hmm .

**Professor C:** So all twenty - five people were sending things to all twenty - five machines

**PhD F:** Mm - hmm . Yeah .

**Professor C:** and {vocalsound} and things were a lot less efficient than if you 'd just use your own machine .

**PhD F:** Yeah . Yep . Yeah , exactly . Yeah , you have to be a little bit careful .

**Professor C:** as I recall , but . Yeah .

**PhD D:** Hmm .

**PhD F:** Um , but uh , you can also {disfmarker} If you have that level of parallelization um , and you don't wanna have to worry about writing the logic in {disfmarker} in a Perl script to take care of that , you can use um , P - make

**Grad G:** Just do P - make .

**PhD F:** and {disfmarker} and you basically write a Make file that uh , you know your final job depends on these one thousand things ,

**Grad G:** s Mm - hmm .

**PhD F:** and when you run P - make , uh , on your Make file , you can give it the dash capital J and {disfmarker} and then a number ,

**Grad G:** Mm - hmm .

**PhD F:** and that number represents how many uh , machines to use at once . And then it 'll make sure that it never goes above that .

**Grad G:** Right .

**PhD F:** So ,

**Grad G:** Right . OK .

**PhD F:** I can get some documentation .

**PhD D:** So it {disfmarker} it 's {disfmarker} it 's not systematically queued . I mean all the jobs are running . If you launch twenty jobs , they are all running . Alright .

**PhD F:** It depends . If you {disfmarker} " Run command " , that I mentioned before , is {disfmarker} doesn't know about other things that you might be running .

**PhD D:** Uh - huh .

**PhD F:** So , it would be possible to run a hundred run jobs at once ,

**PhD D:** Right .

**PhD F:** and they wouldn't know about each other . But if you use P - make , then , it knows about all the jobs that it has to run

**PhD D:** Mm - hmm .

**PhD F:** and it can control , uh , how many it runs simultaneously .

**Professor C:** So " run command " doesn't use P - make , or {disfmarker} ?

**PhD F:** It uses " export " underlyingly . But , if you {disfmarker} i It 's meant to be run one job at a time ? So you could fire off a thousand of those , and it doesn't know {disfmarker} any one of those doesn't know about the other ones that are running .

**Professor C:** So why would one use that rather than P - make ?

**PhD F:** Well , if you have , um {disfmarker} Like , for example , uh if you didn't wanna write a P - make script and you just had a , uh {disfmarker} an HTK training job that you know is gonna take uh , six hours to run , and somebody 's using , uh , the machine you typically use , you can say " run command " and your HTK thing and it 'll find another machine , the fastest currently available machine and {disfmarker} and run your job there .

**Professor C:** Now , does it have the same sort of behavior as P - make , which is that , you know , if you run something on somebody 's machine and they come in and hit a key then it {disfmarker}

**PhD F:** Yes . Yeah , there are um {disfmarker} Right . So some of the machines at the institute , um , have this attribute called " no evict " . And if you specify that , in {disfmarker} in one of your attribute lines , then it 'll go to a machine which your job won't be evicted from .

**Professor C:** Mm - hmm .

**PhD F:** But , the machines that don't have that attribute , if a job gets fired up on that , which could be somebody 's desktop machine , and {disfmarker} and they were at lunch ,

**Professor C:** Mm - hmm .

**PhD F:** they come back from lunch and they start typing on the console , then your machine will get evicted {disfmarker} your job {comment} will get evicted from their machine and be restarted on another machine . Automatically . So {disfmarker} which can cause you to lose time , right ? If you had a two hour job , and it got halfway through and then somebody came back to their machine and it got evicted . So . If you don't want your job to run on a machine where it could be evicted , then you give it the minus {disfmarker} the attribute , you know , " no evict " , and it 'll pick a machine that it can't be evicted from . So .

**Professor C:** Um , what {disfmarker} what about {disfmarker} I remember always used to be an issue , maybe it 's not anymore , that if you {disfmarker} if something required {disfmarker} if your machine required somebody hitting a key in order to evict things that are on it so you could work , but if you were logged into it from home ?

**PhD F:** Mm - hmm .

**Professor C:** and you weren't hitting any keys ? cuz you were , home ?

**PhD F:** Yeah , I {disfmarker} I 'm not sure how that works .

**Professor C:** Yeah .

**PhD F:** Uh , it seems like Andreas did something for that .

**Professor C:** Hmm .

**PhD F:** Um .

**Professor C:** OK . We can ask him sometime .

**PhD F:** But {disfmarker} Yeah . I don't know whether it monitors the keyboard or actually looks at the console TTY , so maybe if you echoed something to the you know , dev {disfmarker} dev console or something .

**Professor C:** You probably wouldn't ordinarily , though . Yeah . Right ? You probably wouldn't ordinarily .

**PhD F:** Hmm ?

**Professor C:** I mean you sort of {disfmarker} you 're at home and you 're trying to log in , and it takes forever to even log you in , and you probably go , " screw this " ,

**PhD F:** Yeah , yeah .

**Professor C:** and {disfmarker} {vocalsound} You know .

**PhD F:** Yeah . Yeah , so , um ,

**Professor C:** Yeah .

**PhD F:** yeah . I {disfmarker} I can {disfmarker} I 'm not sure about that one .

**Professor C:** yeah .

**PhD F:** But uh .

**Professor C:** OK .

**PhD A:** Uh , I need a little orientation about this environment and uh scr s how to run some jobs here because I never d did anything so far with this X emissions

**PhD F:** OK .

**PhD A:** So , I think maybe I 'll ask you after the meeting .

**PhD F:** Um . Yeah . Yeah , and {disfmarker} and also uh , Stephane 's a {disfmarker} a really good resource for that if you can't find me .

**PhD A:** Yeah , yeah , yeah . Yep . OK , sure

**PhD D:** Mmm .

**PhD F:** Especially with regard to the Aurora stuff .

**PhD A:** OK .

**PhD F:** He {disfmarker} he knows that stuff better than I do .

**Professor C:** OK . Well , why don't we uh , uh , Sunil since you 're {vocalsound} haven't {disfmarker} haven't been at one of these yet , why don't yo you tell us what 's {disfmarker} what 's up with you ? Wh - what you 've been up to , hopefully .

**PhD A:** Um . Yeah . So , uh , shall I start from {disfmarker} Well I don't know how may I {disfmarker} how {disfmarker} OK . Uh , I think I 'll start from the post uh Aurora submission maybe .

**Professor C:** Yeah .

**PhD A:** Uh , yeah , after the submission the {disfmarker} what I 've been working on mainly was to take {disfmarker} take other s submissions and then over their system , what they submitted , because we didn't have any speech enhancement system in {disfmarker} in ours . So {disfmarker} So I tried uh , And u First I tried just LDA . And then I found that uh , I mean , if {disfmarker} if I combine it with LDA , it gives @ @ improvement over theirs . Uh {disfmarker}

**PhD F:** Are y are you saying LDA ?

**PhD A:** Yeah . Yeah .

**PhD F:** LDA . OK .

**PhD A:** So , just {disfmarker} just the LDA filters . I just plug in {disfmarker} I just take the cepstral coefficients coming from their system and then plug in LDA on top of that . But the LDA filter that I used was different from what we submitted in the proposal .

**PhD F:** Mm - hmm .

**PhD A:** What I did was {vocalsound} I took the LDA filter 's design using clean speech , uh , mainly because the speech is already cleaned up after the enhancement so , instead of using this , uh , narrow {disfmarker} narrow band LDA filter that we submitted uh , I got new filters . So that seems to be giving {disfmarker} uh , improving over their uh , system . Slightly . But , not very significantly . And uh , that was uh , showing any improvement over {disfmarker} final {disfmarker} by plugging in an LDA . And uh , so then after {disfmarker} after that I {disfmarker} I added uh , on - line normalization also on top of that . And that {disfmarker} there {disfmarker} there also I n I found that I have to make some changes to their time constant that I used because th it has a {disfmarker} a mean and variance update time constant and {disfmarker} which is not suitable for the enhanced speech , and whatever we try it on with proposal - one . But um , I didn't {disfmarker} I didn't play with that time constant a lot , I just t g I just found that I have to reduce the value {disfmarker} I mean , I have to increase the time constant , or reduce the value of the update value . That 's all I found So I have to . Uh , Yeah . And uh , uh , the other {disfmarker} other thing what I tried was , I just um , uh , took the baseline and then ran it with the endpoint inf uh th information , just the Aurora baseline , to see that how much the baseline itself improves by just supplying the information of the {disfmarker} I mean the w speech and nonspeech . And uh , I found that the baseline itself improves by twenty - two percent by just giving the wuh .

**Professor C:** Uh , can you back up a second , I {disfmarker} I {disfmarker} I missed something , uh , I guess my mind wandered . Ad - ad When you added the on - line normalization and so forth , uh , uh things got better again ?

**PhD A:** Yeah . No .

**Professor C:** or is it ?

**PhD A:** No . No , things didn't get better with the same time constant that we used .

**Professor C:** Did it not ? No , no . With a different time constant .

**PhD A:** With the different time constant I found that {disfmarker} I mean , I didn't get an improvement over not using on - line normalization ,

**Professor C:** Oh .

**PhD A:** because I {disfmarker} I found that I would have change the value of the update factor .

**Professor C:** No you didn't , OK .

**PhD A:** But I didn't play it with play {disfmarker} play quite a bit to make it better than .

**Professor C:** Yeah .

**PhD A:** So , it 's still not {disfmarker}

**Professor C:** OK .

**PhD A:** I mean , the on - line normalization didn't give me any improvement .

**Professor C:** OK .

**PhD A:** And uh , so ,

**Professor C:** OK .

**PhD A:** oh yeah So I just stopped there with the uh , speech enhancement . The {disfmarker} the other thing what I tried was the {disfmarker} adding the uh , endpoint information to the baseline and that itself gives like twenty - two percent because the {disfmarker} the second {disfmarker} the new phase is going to be with the endpointed speech . And just to get a feel of how much the baseline itself is going to change by adding this endpoint information , I just , uh , use {disfmarker}

**Professor C:** Hmm .

**PhD F:** So people won't even have to worry about , uh , doing speech - nonspeech then .

**PhD A:** Yeah that 's , that 's what the feeling is like . They 're going to give the endpoint information .

**PhD F:** Mmm .

**Professor C:** G I guess the issue is that people do that anyway ,

**PhD F:** I see .

**Professor C:** everybody does that ,

**PhD A:** Yeah .

**Professor C:** and they wanted to see , given that you 're doing that , what {disfmarker} what are the best features that you should use .

**PhD F:** Yeah , I see .

**PhD A:** So ,

**Professor C:** I mean clearly they 're interact . So I don't know that I entirely agree with it .

**PhD F:** Yeah .

**Professor C:** But {disfmarker} but it might be uh {disfmarker} In some ways it might be better t to {disfmarker} rather than giving the endpoints , to have a standard that everybody uses and then interacts with .

**PhD F:** Mm - hmm .

**Professor C:** But , you know . It 's {disfmarker} it 's still someth reasonable .

**PhD F:** So , are people supposed to assume that there is uh {disfmarker} Are {disfmarker} are people not supposed to use any speech outside of those endpoints ?

**PhD A:** Uh {disfmarker}

**PhD F:** Or can you then use speech outside of it for estimating background noise and things ?

**PhD A:** No . No . That i I {disfmarker} Yeah . Yeah , yeah , exactly . I guess that is {disfmarker} that is where the consensus is . Like y you will {disfmarker} you will {disfmarker} You 'll be given the information about the beginning and the end of speech but the whole speech is available to you .

**PhD F:** OK .

**PhD A:** So .

**Professor C:** So it should make the spectral subtraction style things work even better ,

**PhD A:** Yeah .

**Professor C:** because you don't have the mistakes in it . Yeah ?

**PhD A:** Yeah . So {disfmarker}

**Professor C:** OK .

**PhD A:** So that {disfmarker} that {disfmarker} The baseline itself {disfmarker} I mean , it improves by twenty - two percent . I found that in s one of the SpeechDat - Car cases , that like , the Spanish one improves by just fifty percent by just putting the endpoint . w

**PhD F:** Wow .

**PhD A:** I mean you don't need any further speech enhancement with fifty . So , uh ,

**PhD F:** So the baseline itself improves by fifty percent .

**PhD A:** Yeah , by fifty percent .

**Professor C:** Yeah .

**PhD F:** Wow .

**Professor C:** So it 's g it 's gonna be harder to {vocalsound} beat that actually .

**PhD F:** Yeah .

**PhD A:** Yeah , so {disfmarker}

**Professor C:** But {disfmarker} but {disfmarker}

**PhD A:** so that is when uh , the {disfmarker} the qualification criteria was reduced from fifty percent to something like twenty - five percent for well - matched . And I think they have {disfmarker} they have actually changed their qualification c criteria now . And uh , Yeah , I guess after that , I just went home f I just had a vacation fo for four weeks . Uh .

**Professor C:** OK . No , that 's {disfmarker} that 's {disfmarker} that 's a good {disfmarker} good update .

**PhD A:** Ye Yeah , and I {disfmarker} I came back and I started working on uh , some other speech enhancement algorithm . I mean , so {disfmarker} I {disfmarker} from the submission what I found that people have tried spectral subtraction and Wiener filtering . These are the main uh , approaches where people have tried ,

**Professor C:** Yeah .

**PhD A:** so just to {disfmarker} just to fill the space with some f few more speech enhancement algorithms to see whether it improves a lot , I {disfmarker} I 've been working on this uh , signal subspace approach for speech enhancement where you take the noisy signal and then decomposing the signal s and the noise subspace and then try to estimate the clean speech from the signal plus noise subspace . And {disfmarker}

**Professor C:** Mm - hmm .

**PhD A:** So , I 've been actually running some s So far I 've been trying it only on Matlab . I have to {disfmarker} to {disfmarker} to test whether it works first or not

**Professor C:** Yeah .

**PhD A:** and then I 'll p port it to C and I 'll update it with the repository once I find it it giving any some positive result . So , yeah .

**Professor C:** S So you s you So you said one thing I want to jump on for a second . So {disfmarker} so now you 're {disfmarker} you 're getting tuned into the repository thing that he has here

**PhD A:** Yeah .

**Professor C:** and {disfmarker} so we we 'll have a {vocalsound} single place where the stuff is .

**PhD A:** Yep . Yeah .

**Professor C:** Cool . Um , so maybe uh , just briefly , you could remind us about the related experiments . Cuz you did some stuff that you talked about last week , I guess ?

**PhD D:** Mm - hmm .

**Professor C:** Um , where you were also combining something {disfmarker} both of you I guess were both combining something from the uh , French Telecom system with {vocalsound} the u uh {disfmarker}

**PhD D:** Right .

**Professor C:** I {disfmarker} I don't know whether it was system one or system two , or {disfmarker} ?

**PhD D:** Mm - hmm . It was system one . So

**Professor C:** OK .

**PhD D:** we {disfmarker} The main thing that we did is just to take the spectral subtraction from the France Telecom , which provide us some speech samples that are uh , with noise removed .

**Professor C:** So I let me {disfmarker} let me just stop you there . So then , one distinction is that uh , you were taking the actual France Telecom features and then applying something to {disfmarker}

**PhD A:** Uh , no there is a slight different . Uh I mean , which are extracted at the handset because they had another back - end blind equalization {disfmarker}

**Professor C:** Yeah .

**PhD A:** Yeah .

**Professor C:** Yeah . But that 's what I mean .

**PhD A:** Yeah .

**Professor C:** But u u Sorry ,

**PhD A:** Yeah .

**Professor C:** yeah , I 'm not being {disfmarker} I 'm not being clear .

**PhD A:** Yeah .

**Professor C:** What I meant was you had something like cepstra or something , right ?

**PhD A:** Yeah , yeah , yeah , yeah .

**Professor C:** And so one difference is that , I guess you were taking spectra .

**PhD A:** The speech .

**PhD B:** Yeah .

**PhD D:** Yeah . But I guess it 's the s exactly the same thing because on the heads uh , handset they just applied this Wiener filter and then compute cepstral features ,

**PhD A:** Yeah , the cepstral f The difference is like {disfmarker} There may be a slight difference in the way {disfmarker}

**PhD D:** right ? or {disfmarker} ?

**PhD A:** because they use exactly the baseline system for converting the cepstrum once you have the speech . I mean , if we are using our own code for th I mean that {disfmarker} that could be the only difference .

**PhD D:** Right .

**PhD A:** I mean , there is no other difference .

**PhD D:** Mm - hmm .

**PhD A:** Yeah .

**Professor C:** But you got some sort of different result . So I 'm trying to understand it . But uh , I th

**PhD D:** Yeah , well I think we should uh , have a table with all the result because I don't know I uh , I don't exactly know what are your results ? But ,

**PhD A:** OK . OK .

**PhD D:** Mmm . Yeah , but so we did this , and another difference I guess is that we just applied uh , proposal - one system after this without {disfmarker} well , with our modification to reduce the delay of the {disfmarker} the LDA filters ,

**PhD A:** Uh - huh .

**PhD D:** and

**PhD B:** And the filter {disfmarker}

**PhD D:** Well there are slight modifications , but it was the full proposal - one . In your case , if you tried just putting LDA , then maybe on - line normalization {disfmarker} ?

**PhD A:** Only LDA . Yeah . Af - I {disfmarker} after that I added on - line normalization , yeah .

**PhD D:** Mm - hmm . So we just tried directly to {disfmarker} to just , keep the system as it was and , um , when we plug the spectral subtraction it improves uh , signif significantly . Um , but , what seems clear also is that we have to retune the time constants of the on - line normalization .

**PhD A:** Yeah , yeah . Yeah .

**PhD D:** Because if we keep the value that was submitted uh , it doesn't help at all . You can remove on - line normalization , or put it , it doesn't change anything . Uh , uh , as long as you have the spectral subtraction . But , you can still find some kind of optimum somewhere , and we don't know where exactly

**PhD A:** Yeah .

**PhD D:** but , uh .

**PhD A:** Yeah , I assume .

**Professor C:** So it sounds like you should look at some tables of results or something

**PhD D:** Right .

**PhD A:** Yeah .

**PhD D:** Yeah .

**Professor C:** and see where i where the {disfmarker} {vocalsound} where they were different and what we can learn from it .

**PhD D:** Mm - hmm . Mm - hmm .

**PhD A:** without any change . OK .

**PhD B:** But it 's {disfmarker}

**PhD D:** Yeah . Well ,

**PhD B:** It 's the new .

**PhD D:** with {disfmarker} with {disfmarker} with changes ,

**PhD A:** with

**PhD B:** The new .

**PhD D:** because we change it the system to have {disfmarker}

**PhD A:** Oh yeah , I mean the {disfmarker} the new LDA filters .

**PhD B:** The new .

**PhD A:** I mean {disfmarker} OK .

**PhD D:** Yeah . LDA filters . There are other things that we finally were shown to improve also like , the sixty - four hertz cut - off .

**PhD A:** Mm - hmm .

**PhD B:** Mm - hmm .

**PhD D:** w Uh , it doesn't seem to hurt on TI - digits , finally .

**PhD A:** OK .

**PhD D:** Maybe because of other changes .

**PhD A:** OK .

**PhD D:** Um , well there are some {vocalsound} minor changes , yeah .

**PhD A:** Mm - hmm .

**PhD D:** And , right now if we look at the results , it 's , um , always better than {disfmarker} it seems always better than France Telecom for mismatch and high - mismatch . And it 's still slightly worse for well - matched .

**PhD B:** But

**PhD D:** Um , but this is not significant . But , the problem is that it 's not significant , but if you put this in the , mmm , uh , spreadsheet , it 's still worse . Even with very minor {disfmarker} uh , even if it 's only slightly worse for well - matched .

**Professor C:** Mm - hmm .

**PhD D:** And significantly better for HM . Uh , but , well . I don't think it 's importa important because when they will change their metric , uh , uh , mainly because of uh , when you p you plug the um , frame dropping in the baseline system , it will improve a lot HM , and MM ,

**PhD A:** Yeah .

**PhD D:** so , um , I guess what will happen {disfmarker} I don't know what will happen . But , the different contribution , I think , for the different test set will be more even .

**PhD A:** Because the {disfmarker} your improvement on HM and MM will also go down significantly in the spreadsheet so . But the {pause} the well - matched may still {disfmarker}

**PhD D:** Mm - hmm .

**PhD A:** I mean the well - matched may be the one which is least affected by adding the endpoint information .

**Professor C:** Right .

**PhD A:** Yeah . So the {disfmarker} the MM {disfmarker}

**PhD D:** Mm - hmm .

**PhD A:** MM and HM are going to be v hugely affected by it . Yeah .

**PhD D:** Yeah , so um , yeah .

**PhD A:** Yeah . But they d the {disfmarker} everything I mean is like , but there that 's how they reduce {disfmarker} why they reduce the qualification to twenty - five percent or some {disfmarker} something on .

**PhD D:** Mm - hmm .

**Professor C:** But are they changing the weighting ?

**PhD A:** Uh , no , I guess they are going ahead with the same weighting .

**PhD D:** Yeah .

**PhD A:** Yeah . So there 's nothing on {disfmarker}

**Professor C:** I don't understand that .

**PhD A:** Yeah .

**Professor C:** I guess I {disfmarker} I haven't been part of the discussion , so , um , it seems to me that the well - matched condition is gonna be unusual ,

**PhD A:** Usual .

**Professor C:** in this case . Unusual .

**PhD A:** Uh - huh .

**Professor C:** Because , um , you don't actually have good matches ordinarily for what any @ @ {disfmarker} particular person 's car is like , or

**PhD A:** Mmm .

**Professor C:** uh ,

**PhD A:** Mmm .

**Professor C:** It seems like something like the middle one is {disfmarker} is more natural .

**PhD A:** Hmm . Right .

**Professor C:** So I don't know why the {pause} well - matched is uh {disfmarker}

**PhD D:** Mm - hmm .

**PhD A:** Yeah , but actually the well {disfmarker} well the well - matched um , uh , I mean the {disfmarker} the well - matched condition is not like , uh , the one in TI - digits where uh , you have all the training , uh , conditions exactly like replicated in the testing condition also . It 's like , this is not calibrated by SNR or something . The well - matched has also some {disfmarker} some mismatch in that which is other than the {disfmarker}

**Professor C:** The well wa matched has mismatch ?

**PhD A:** has {disfmarker} has also some slight mismatches , unlike the TI - digits where it 's like prefectly matched

**PhD F:** Perfect to match .

**PhD A:** because it 's artificially added noise .

**Professor C:** Yeah .

**PhD A:** But this is natural recording .

**Professor C:** Yeah . So remind me of what well - matched meant ?

**PhD A:** The {disfmarker} the well - matched is like {disfmarker}

**Professor C:** You 've told me many times .

**PhD A:** the {disfmarker} the well - matched is defined like it 's seventy percent of the whole database is used for training and thirty percent for testing .

**PhD D:** Yeah . Well , so it means that if the database is large enough , it 's matched .

**PhD A:** It 's {disfmarker} it 's {disfmarker}

**PhD D:** Because it

**PhD A:** OK , it 's {disfmarker}

**Professor C:** Yeah .

**PhD D:** in each set you have a range of conditions {disfmarker} Well {disfmarker}

**Professor C:** Right . So , I mean , yeah , unless they deliberately chose it to be different , which they didn't because they want it to be well - matched , it is pretty much {disfmarker} You know , so it 's {disfmarker} so it 's sort of saying if you {disfmarker}

**PhD F:** It 's {disfmarker} it 's not guaranteed though .

**PhD A:** Yeah .

**Professor C:** Uh , it 's not guaranteed .

**PhD A:** Yeah .

**Professor C:** Right .

**PhD D:** Mm - hmm .

**PhD A:** Yeah because the m the main {disfmarker} major reason for the m

**Professor C:** Right .

**PhD A:** the main mismatch is coming from the amount of noise and the silence frames and all those present in the database actually .

**Professor C:** Again , if you have enough {disfmarker} if you have enough {disfmarker}

**PhD A:** No yeah , yeah . Yeah .

**Professor C:** So it 's sort of i i it 's sort of saying OK , so you {disfmarker} much as you train your dictation machine for talking into your computer , um , you {disfmarker} you have a car , and so you drive it around a bunch and {disfmarker} and record noise conditions , or something , and then {disfmarker} I don't think that 's very realistic , I mean I th

**PhD A:** Mm - hmm .

**Professor C:** I {disfmarker} I you know , so I {disfmarker} I {disfmarker} I {disfmarker} you know , I guess they 're saying that if you were a company that was selling the stuff commercially , that you would have a bunch of people driving around in a bunch of cars , and {disfmarker} and you would have something that was roughly similar and maybe that 's the argument , but I 'm not sure I buy it , so .

**PhD A:** Yeah , yeah , yeah .

**Professor C:** Uh , So What else is going on ?

**PhD D:** Mmm . You Yeah . We are playing {disfmarker} we are also playing , trying to put other spectral subtraction mmm , in the code . Um , it would be a very simple spectral subtraction , on the um , mel energies which I already tested but without the um frame dropping actually , and I think it 's important to have frame dropping if you use spectral subtraction .

**PhD F:** Is it {disfmarker} is spectral subtraction typically done on the {disfmarker} after the mel , uh , scaling or is it done on the FFT bins ?

**PhD D:** Um ,

**PhD F:** Does it matter , or {disfmarker} ?

**PhD D:** I d I don't know . Well , it 's both {disfmarker} both uh , cases can i

**PhD F:** Oh .

**PhD D:** Yeah . So - some of the proposal , uh , we 're doing this on the bin {disfmarker} on the FFT bins ,

**PhD F:** Hmm .

**PhD D:** others on the um , mel energies . You can do both , but I cannot tell you what 's {disfmarker} which one might be better or {disfmarker} I {disfmarker}

**PhD F:** Hmm .

**PhD A:** I guess if you want to reconstruct the speech , it may be a good idea to do it on FFT bins .

**PhD D:** I don't know . Yeah , but

**PhD F:** Mmm .

**PhD A:** But for speech recognition , it may not . I mean it may not be very different if you do it on mel warped or whether you do it on FFT . So you 're going to do a linear weighting anyway after that .

**PhD F:** I see .

**PhD A:** Well {disfmarker} Yeah ?

**PhD F:** Hmm .

**PhD A:** So , it may not be really a big different .

**PhD D:** Well , it gives something different , but I don't know what are the , pros and cons of both .

**PhD A:** It I Uh - huh .

**Professor C:** Hmm .

**PhD A:** So

**Professor C:** OK .

**PhD A:** The other thing is like when you 're putting in a speech enhancement technique , uh , is it like one stage speech enhancement ? Because everybody seems to have a mod two stages of speech enhancement in all the proposals , which is really giving them some improvement .

**PhD D:** Yeah .

**PhD B:** Mm - hmm .

**PhD D:** Mm - hmm .

**PhD A:** I mean they just do the same thing again once more .

**Professor C:** Mm - hmm .

**PhD A:** And {disfmarker} So , there 's something that is good about doing it {disfmarker} I mean , to cleaning it up once more .

**PhD D:** Yeah , it might be .

**PhD A:** Yeah ,

**PhD D:** Yeah .

**PhD A:** so we can {disfmarker}

**PhD D:** So maybe in my implementation I should also try to inspire me from this kind of thing

**PhD A:** Yeah . That 's what

**Professor C:** Well , the other thing would be to combine what you 're doing .

**PhD D:** and {disfmarker} Yeah .

**Professor C:** I mean maybe one or {disfmarker} one or the other of the things that you 're doing would benefit from the other happening first .

**PhD A:** That 's wh Yeah . So ,

**Professor C:** Right , so he 's doing a signal subspace thing , maybe it would work better if you 'd already done some simple spectral subtraction , or maybe vi maybe the other way around ,

**PhD D:** Yeah , mm - hmm .

**PhD A:** Yeah .

**Professor C:** you know ?

**PhD A:** So I 've been thinking about combining the Wiener filtering with signal subspace ,

**PhD D:** Mm - hmm .

**PhD A:** I mean just to see all {disfmarker} some {disfmarker} some such permutation combination to see whether it really helps or not .

**PhD D:** Mm - hmm . Mm - hmm . Mm - hmm . Yeah . Yeah .

**Professor C:** How is it {disfmarker} I {disfmarker} I guess I 'm ignorant about this , how does {disfmarker} I mean , since Wiener filter also assumes that you 're {disfmarker} that you 're adding together the two signals , how is {disfmarker} how is that differ from signal subspace ?

**PhD A:** The signal subspace ? The {disfmarker}

**Professor C:** Yeah .

**PhD A:** The signal subspace approach has actually an in - built Wiener filtering in it .

**Professor C:** Oh , OK .

**PhD A:** Yeah . It is like a KL transform followed by a Wiener filter . Is the signal is {disfmarker} is a signal substrate .

**Professor C:** Oh , oh , OK so the difference is the KL .

**PhD A:** So , the {disfmarker} the different {disfmarker} the c the {disfmarker} the advantage of combining two things is mainly coming from the signal subspace approach doesn't work very well if the SNR is very bad . It 's {disfmarker} it works very poorly with the poor SNR conditions , and in colored noise .

**Professor C:** I see . So essentially you could do simple spectral subtraction , followed by a KL transform , followed by a

**PhD A:** Wiener filtering . It 's a {disfmarker} it 's a cascade of two s

**Professor C:** Wiener filter . Yeah , in general , you don't {disfmarker} that 's right you don't wanna othorg orthogonalize if the things are noisy . Actually . Um , that was something that uh , Herve and I were talking about with um , the multi - band stuff , that if you 're converting things to from uh , bands , groups of bands into cepstral coef you know , local sort of local cepstral coefficients that it 's not that great to do it if it 's noisy .

**PhD A:** Mm - hmm . OK . Yeah . So .

**Professor C:** Uh , so .

**PhD A:** So that {disfmarker} that 's one reason maybe we could combine s some {disfmarker} something to improve SNR a little bit , first stage ,

**Professor C:** Yeah .

**PhD A:** and then do a something in the second stage which could take it further .

**PhD D:** What was your point about {disfmarker} about colored noise there ?

**PhD A:** Oh , the colored noise uh {disfmarker}

**PhD D:** Yeah .

**PhD A:** the colored noise {disfmarker} the {disfmarker} the v the signal subspace approach has {disfmarker} I mean , it {disfmarker} it actually depends on inverting the matrices . So it {disfmarker} it {disfmarker} ac the covariance matrix of the noise . So if {disfmarker} if it is not positive definite ,

**PhD D:** Mm - hmm .

**PhD A:** I mean it has a {disfmarker} it 's {disfmarker} It doesn't behave very well if it is not positive definite ak It works very well with white noise because we know for sure that it has a positive definite .

**Professor C:** So you should do spectral subtraction and then add noise .

**PhD A:** So the way they get around is like they do an inverse filtering , first of the colo colored noise

**Professor C:** Yeah .

**PhD A:** and then make the noise white ,

**Professor C:** Yeah .

**PhD A:** and then finally when you reconstruct the speech back , you do this filtering again .

**PhD D:** Yeah , right .

**Professor C:** I was only half kidding . I mean if you {disfmarker} sort of {vocalsound} you do the s spectral subtraction , that also gets rid {disfmarker}

**PhD A:** Yeah .

**PhD D:** Yeah .

**PhD A:** Yeah .

**Professor C:** and then you {disfmarker} then {disfmarker} then add a little bit l noise {disfmarker} noise addition {disfmarker} I mean , that sort of what J {disfmarker} JRASTA does , in a way .

**PhD A:** Yeah .

**Professor C:** If you look at what JRASTA doing essentially i i it 's equivalent to sort of adding a little {disfmarker} adding a little noise ,

**PhD A:** Huh ? Uh - huh .

**PhD D:** Uh - huh .

**Professor C:** in order to get rid of the effects of noise .

**PhD A:** So .

**Professor C:** OK .

**PhD D:** Yeah . Uh , yeah . So there is this . And maybe we {disfmarker} well we find some people so that {vocalsound} uh , agree to maybe work with us , and they have implementation of VTS techniques so it 's um , Vector Taylor Series that are used to mmm , {vocalsound} uh f to model the transformation between clean cepstra and noisy cepstra . So . Well , if you take the standard model of channel plus noise , uh , it 's {disfmarker} it 's a nonlinear eh uh , transformation in the cepstral domain .

**Professor C:** Mm - hmm . Yes .

**PhD D:** And uh , there is a way to approximate this using uh , first - order or second - order Taylor Series and it can be used for {vocalsound} uh , getting rid of the noise and the channel effect .

**Professor C:** Who is doing this ?

**PhD D:** Uh w working in the cepstral domain ? So there is one guy in Grenada ,

**PhD B:** Yeah , in Grenada one of my friend .

**PhD D:** and another in {pause} uh , Lucent that I met at ICASSP .

**Professor C:** Who 's the guy in Grenada ?

**PhD D:** uh ,

**PhD B:** Uh , Jose Carlos Segura .

**Professor C:** I don't know him .

**PhD A:** This VTS has been proposed by CMU ?

**PhD D:** Mm - hmm .

**PhD A:** Is it {disfmarker} is it the CMU ? Yeah , yeah , OK .

**PhD B:** Yeah , yeah , yeah . Originally the idea was from CMU .

**PhD A:** From C .

**PhD D:** Mm - hmm . Yeah .

**Professor C:** Uh - huh .

**PhD D:** Well , it 's again a different thing {vocalsound} {vocalsound} that could be tried . Um ,

**Professor C:** Uh - huh .

**PhD D:** Mmm , yeah .

**Professor C:** Yeah , so at any rate , you 're looking general , uh , standing back from it , looking at ways to combine one form or another of uh , noise removal , uh , with {disfmarker} with these other things we have ,

**PhD D:** Mm - hmm .

**Professor C:** uh , looks like a worthy thing to {disfmarker} to do here .

**PhD D:** Uh , yeah . But , yeah . But for sure there 's required to {disfmarker} that requires to re - check everything else , and re - optimize the other things

**Professor C:** Oh yeah .

**PhD D:** and , for sure the on - line normalization may be the LDA filter . Um ,

**Professor C:** Well one of the {disfmarker} seems like one of the things to go through next week when Hari 's here ,

**PhD D:** I {disfmarker}

**Professor C:** cuz Hari 'll have his own ideas too {disfmarker} or {pause} I guess not next week ,

**PhD D:** Uh - huh .

**Professor C:** week and a half , uh , will be sort of go through these alternatives , what we 've seen so far , and come up with some game plans . Um . You know . So , I mean one way would {disfmarker} he Here are some alternate visions . I mean one would be , you look at a few things very quickly , you pick on something that looks like it 's promising and then everybody works really hard on the same {disfmarker} different aspects of the same thing . Another thing would be to have t to {disfmarker} to pick two pol two plausible things , and {disfmarker} and you know , have t sort of two working things for a while until we figure out what 's better ,

**PhD D:** Mm - hmm .

**Professor C:** and then , you know , uh , but , w um , uh , he 'll have some ideas on that too .

**PhD A:** The other thing is to , uh {disfmarker} Most of the speech enhancement techniques have reported results on small vocabulary tasks . But we {disfmarker} we going to address this Wall Street Journal in our next stage , which is also going to be a noisy task so s very few people have reported something on using some continuous speech at all . So , there are some {disfmarker} I mean , I was looking at some literature on speech enhancement applied to large vocabulary tasks and spectral subtraction doesn't seems to be the thing to do for large vocabulary tasks . And it 's {disfmarker} Always people have shown improvement with Wiener filtering and maybe subspace approach over spectral subtraction everywhere . But if we {disfmarker} if we have to use simple spectral subtraction , we may have to do some optimization {pause} to make it work @ @ .

**Professor C:** So they 're making {disfmarker} there {disfmarker} Somebody 's generating Wall Street Journal with additive {disfmarker} artificially added noise or something ?

**PhD A:** Yeah , yeah .

**Professor C:** Sort of a {disfmarker} sort of like what they did with TI - digits , and ?

**PhD A:** Yeah . Yeah .

**Professor C:** Yeah , OK .

**PhD A:** I m I guess Guenter Hirsch is in charge of that . Guenter Hirsch and TI .

**Professor C:** OK .

**PhD A:** Maybe Roger {disfmarker} r Roger , maybe in charge of .

**Professor C:** And then they 're {disfmarker} they 're uh , uh , generating HTK scripts to {disfmarker}

**PhD A:** Yeah . Yeah , I don't know . There are {disfmarker} they have {disfmarker} there is no {disfmarker} I don't know if they are converging on HTK or are using some Mississippi State ,

**Professor C:** Mis - Mississippi State maybe ,

**PhD A:** yeah . I 'm not sure about that .

**Professor C:** yeah . Yeah , so that 'll be a little {disfmarker} little task in itself .

**PhD A:** Yeah .

**Professor C:** Um , well we 've {disfmarker} Yeah , it 's true for the additive noise , y artificially added noise we 've always used small vocabulary too . But for n there 's been noisy speech this larv large vocabulary that we 've worked with in Broadcast News . So we we did the Broadcast News evaluation

**PhD A:** Mm - hmm .

**Professor C:** and some of the focus conditions were noisy and {disfmarker} and {disfmarker}

**PhD A:** It had additive n

**Professor C:** But we {disfmarker} but we didn't do spectral subtraction . We were doing our funny stuff , right ? We were doing multi multi uh , multi - stream and {disfmarker} and so forth .

**PhD A:** Yeah .

**Professor C:** But it , you know , we di stuff we did helped . I mean it , did something .

**PhD A:** OK .

**Professor C:** So . Um , now we have this um , meeting data . You know , like the stuff we 're {comment} recording right now ,

**PhD A:** Yeah . Yeah .

**Professor C:** and {disfmarker} and uh , that we have uh , for the {disfmarker} uh , the quote - unquote noisy data there is just {disfmarker} noisy and reverberant actually . It 's the far field mike . And uh , we have uh , the digits that we do at the end of these things . And that 's what most o again , most of our work has been done with that , with {disfmarker} with uh , connected digits .

**PhD A:** Uh - huh .

**Professor C:** Um , but uh , we have recognition now with some of the continuous speech , large vocabulary continuous speech , using Switchboard {disfmarker} uh , Switchboard recognizer ,

**PhD A:** Yeah . OK .

**Professor C:** uh , no training , {vocalsound} from this , just {disfmarker} just plain using the Switchboard .

**PhD A:** Oh . You just take the Switchboard trained {disfmarker} ? Yeah ,

**Professor C:** That 's {disfmarker} that 's what we 're doing ,

**PhD A:** yeah .

**Professor C:** yeah . Now there are some adaptation though ,

**PhD A:** OK . Yeah . That 's cool .

**Professor C:** that {disfmarker} that uh , Andreas has been playing with ,

**PhD A:** OK .

**Professor C:** but we 're hop uh , actually uh , Dave and I were just talking earlier today about maybe at some point not that distant future , trying some of the techniques that we 've talked about on , uh , some of the large vocabulary data . Um , I mean , I guess no one had done {disfmarker} yet done test one on the distant mike using uh , the SRI recognizer and , uh ,

**PhD F:** I don't {disfmarker} not that I know of .

**Professor C:** Yeah , cuz everybody 's scared .

**PhD A:** Yeah .

**Professor C:** You 'll see a little smoke coming up from the {disfmarker} the CPU or something {vocalsound} trying to {disfmarker} trying to do it ,

**PhD F:** That 's right

**Professor C:** but uh , yeah . But , you 're right that {disfmarker} that {disfmarker} that 's a real good point , that uh , we {disfmarker} we don't know yeah , uh , I mean , what if any of these ta I guess that 's why they 're pushing that in the uh {disfmarker} in the evaluation .

**PhD A:** Yeah .

**Professor C:** Uh , But um , Good . OK . Anything else going on ? at you guys ' end ,

**PhD B:** I don't have good result , with the {disfmarker} inc including the new parameters ,

**Professor C:** or {disfmarker} ?

**PhD B:** I don't have good result . Are {pause} similar or a little bit worse .

**PhD A:** With what {disfmarker} what other new p new parameter ?

**Grad G:** You 're talking about your voicing ?

**Professor C:** Yeah .

**PhD B:** Yeah .

**Professor C:** So maybe {disfmarker} You probably need to back up a bit

**PhD A:** Yeah .

**PhD B:** Mm - hmm .

**Professor C:** seeing as how Sunil ,

**PhD B:** I tried to include another new parameter to the traditional parameter ,

**Professor C:** yeah .

**PhD B:** the coe the cepstrum coefficient ,

**PhD A:** Uh - huh .

**PhD B:** that , like , the auto - correlation , the R - zero and R - one over R - zero

**PhD A:** Mm - hmm . Mm - hmm .

**PhD B:** and another estimation of the var the variance of the difference for {disfmarker} of the spec si uh , spectrum of the signal and {disfmarker} and the spectrum of time after filt mel filter bank .

**PhD A:** I 'm so sorry . I didn't get it .

**PhD B:** Nuh . Well . Anyway . The {disfmarker} First you have the sp the spectrum of the signal ,

**PhD A:** Mm - hmm .

**PhD B:** and you have the {disfmarker} on the other side you have the output of the mel filter bank .

**PhD A:** Mm - hmm .

**PhD B:** You can extend the coefficient of the mel filter bank and obtain an approximation of the spectrum of the signal .

**PhD A:** Mmm . OK .

**PhD B:** I do the difference {disfmarker}

**PhD A:** OK .

**PhD B:** I found a difference at the variance of this different

**PhD A:** Uh - huh .

**PhD B:** because , suppose we {disfmarker} we think that if the variance is high , maybe you have n uh , noise .

**PhD A:** Yeah .

**PhD B:** And if the variance is small , maybe you have uh , speech .

**PhD A:** Uh - huh .

**PhD B:** To {disfmarker} to To {disfmarker} The idea is to found another feature for discriminate between voice sound and unvoice sound .

**PhD A:** OK .

**PhD B:** And we try to use this new feature {disfmarker} feature . And I did experiment {disfmarker} I need to change {disfmarker} to obtain this new feature I need to change the size {disfmarker} the window size {disfmarker} size . of the a of the {disfmarker} analysis window size , to have more information .

**PhD A:** Yeah . Make it longer .

**PhD B:** Uh , sixty - two point five milliseconds I think .

**PhD A:** OK .

**PhD B:** And I do {disfmarker} I did two type of experiment to include this feature directly with the {disfmarker} with the other feature and to train a neural network to select it voice - unvoice - silence {disfmarker} silence

**PhD A:** Unvoiced . Well .

**PhD B:** and to {disfmarker} to concat this new feature . But the result are n with the neural network I have more or less the same result .

**PhD A:** As using just the cepstrum ,

**PhD B:** Result .

**PhD A:** or {disfmarker} ?

**PhD B:** Yeah .

**PhD A:** OK .

**PhD B:** Yeah . It 's neve e e sometime it 's worse , sometime it 's a little bit better , but not significantly .

**PhD A:** Uh , is it with TI - digits , or with {disfmarker} ?

**PhD B:** And {disfmarker} No , I work with eh , Italian and Spanish basically .

**PhD A:** OK . OK .

**PhD B:** And if I don't y use the neural network , and use directly the feature the results are worse .

**PhD A:** Uh - huh .

**PhD B:** But Doesn't help .

**Professor C:** I {disfmarker} I {disfmarker} I really wonder though .

**PhD D:** Mm - hmm .

**Professor C:** I mean we 've had these discussions before , and {disfmarker} and one of the things that struck me was that {disfmarker} uh , about this line of thought that was particularly interesting to me was that we um {disfmarker} whenever you condense things , uh , in an irreversible way , um , you throw away some information . And , that 's mostly viewed on as a good thing , in the way we use it , because we wanna suppress things that will cause variability for uh particular , uh , phonetic units . Um , but , you 'll do throw something away . And so the question is , uh , can we figure out if there 's something we 've thrown away that we shouldn't have . And um . So , when they were looking at the difference between the filter bank and the FFT that was going into the filter bank , I was thinking " oh , OK , so they 're picking on something they 're looking on it to figure out noise , or voice {disfmarker} voiced property whatever . " So that {disfmarker} that 's interesting . Maybe that helps to drive the {disfmarker} the thought process of coming up with the features . But for me sort of the interesting thing was , " well , but is there just something in that difference which is useful ? " So another way of doing it , maybe , would be just to take the FFT uh , power spectrum , and feed it into a neural network ,

**PhD B:** To know {disfmarker}

**Professor C:** and then use it , you know , in combination , or alone , or {disfmarker} or whatever

**PhD F:** Wi - with what targets ?

**PhD A:** Voiced , unvoiced is like {disfmarker}

**Professor C:** Uh , no .

**PhD A:** Oh . Or anything .

**Professor C:** No the {disfmarker} just the same {disfmarker} same way we 're using {disfmarker} I mean , the same way that we 're using the filter bank .

**PhD F:** Phones .

**PhD A:** Oh , OK .

**Professor C:** Exact way {disfmarker} the same way we 're using the filter bank .

**PhD D:** Mm - hmm .

**Professor C:** I mean , the filter bank is good for all the reasons that we say it 's good . But it 's different . And , you know , maybe if it 's used in combination , it will get at something that we 're missing . And maybe , you know , using , orth you know , KLT , or uh , um , adding probabilities , I mean , all th all the different ways that we 've been playing with , that we would let the {disfmarker} essentially let the neural network determine what is it that 's useful , that we 're missing here .

**PhD D:** Mm - hmm . Mm - hmm .

**PhD A:** Mm - hmm .

**PhD D:** Yeah , but there is so much variability in the power spectrum .

**Professor C:** Well , that 's probably why y i it would be unlikely to work as well by itself , but it might help in combination .

**PhD D:** Mm - hmm . Mmm .

**Professor C:** But I {disfmarker} I {disfmarker} I have to tell you , I can't remember the conference , but , uh , I think it 's about ten years ago , I remember going to one of the speech conferences and {disfmarker} and uh , I saw within very short distance of one another a couple different posters that showed about the wonders of some auditory inspired front - end or something , and a couple posters away it was somebody who compared one to uh , just putting in the FFT and the FFT did slightly better . So I mean the {disfmarker} i i It 's true there 's lots of variability ,

**PhD D:** Mm - hmm .

**Professor C:** but again we have these wonderful statistical mechanisms for quantifying that a that variability , and you know , doing something reasonable with it .

**PhD D:** Mm - hmm .

**Professor C:** So , um , uh , It - it 's same , you know , argument that 's gone both ways about uh , you know , we have these data driven filters , in LDA , and on the other hand , if it 's data driven it means it 's driven by things that have lots of variability , and that are necessarily {disfmarker} not necessarily gonna be the same in training and test , so , in some ways it 's good to have data driven things , and in some ways it 's bad to have data driven things . So ,

**PhD A:** Yeah , d

**Professor C:** part of what we 're discovering , is ways to combine things that are data driven than are not .

**PhD A:** Yeah .

**Professor C:** Uh , so anyway , it 's just a thought , that {disfmarker} that if we {disfmarker} if we had that {disfmarker} maybe it 's just a baseline uh , which would show us " well , what are we really getting out of the filters " , or maybe i i probably not by itself , but in combination , uh ,

**PhD D:** Mm - hmm .

**Professor C:** you know , maybe there 's something to be gained from it , and let the {disfmarker} But , you know , y you 've only worked with us for a short time , maybe in a year or two you w you will actually come up with the right set of things to extract from this information . But , maybe the neural net and the H M Ms could figure it out quicker than you .

**PhD B:** Maybe .

**Professor C:** So .

**PhD B:** Yeah ,

**Professor C:** It 's just a thought .

**PhD B:** I can {disfmarker} I will try to do that .

**Professor C:** Yeah .

**PhD A:** What {disfmarker} one {disfmarker} one um p one thing is like what {disfmarker} before we started using this VAD in this Aurora , the {disfmarker} th what we did was like , I {disfmarker} I guess most of you know about this , adding this additional speech - silence bit to the cepstrum and training the HMM on that .

**Professor C:** Mm - hmm .

**PhD A:** That is just a binary feature and that seems to be {vocalsound} improving a lot on the SpeechDat - Car where there is a lot of noise but not much on the TI - digits . So , a adding an additional feature to distin to discriminate between speech and nonspeech was helping . That 's it .

**PhD D:** Wait {disfmarker} I {disfmarker} I 'm sorry ?

**PhD A:** Yeah , we actually added an additional binary feature to the cepstrum , just the baseline .

**PhD D:** Yeah ?

**PhD B:** You did some experiment .

**PhD A:** Yeah , yeah . Well , in {disfmarker} in the case of TI - digits it didn't actually give us anything , because there wasn't any f anything to discriminate between speech ,

**PhD D:** Yeah .

**PhD A:** and it was very short . But Italian was like very {disfmarker} it was a huge improvement on Italian .

**PhD D:** Hmm . Well {disfmarker} Mm - hmm . But anyway the question is even more , is within speech , can we get some features ? Are we drop dropping information that can might be useful within speech ,

**PhD A:** OK .

**PhD D:** I mean . To {disfmarker} maybe to distinguish between voice sound and unvoiced sounds ?

**PhD A:** Mm - hmm . Yeah , yeah . Yeah .

**Professor C:** And it 's particularly more relevant now since we 're gonna be given the endpoints .

**PhD D:** Yeah .

**Professor C:** So .

**PhD D:** Mm - hmm .

**PhD A:** Yeah , yeah .

**Professor C:** Uh . So .

**PhD D:** Mmm .

**PhD A:** Mmm .

**Professor C:** Um .

**PhD A:** There was a paper in ICASSP {disfmarker} this ICASSP {disfmarker} over the uh extracting some higher - order uh , information from the cepstral coefficients and I forgot the name . Some is some harmonics I don't know , I can {disfmarker} I can pull that paper out from ICASSP . It {disfmarker}

**Professor C:** Talking cumulants or something ?

**PhD D:** Yeah .

**PhD A:** Huh ? Uh , I don't know .

**Professor C:** Cumulants or something .

**PhD A:** I don't remember .

**Professor C:** But {disfmarker} No .

**PhD A:** It wa it was taking the , um {disfmarker} It was about finding the higher - order moments of {disfmarker} Yeah .

**Professor C:** Yeah ,

**PhD A:** And I 'm not sure about whether it is the higher - order moments , or {disfmarker}

**Professor C:** cumulants , yeah .

**PhD A:** maybe higher - order cumulants

**Professor C:** Oh .

**PhD A:** and {disfmarker} Yeah . It was {disfmarker} it was {disfmarker}

**Professor C:** Or m e

**PhD A:** Yeah . I mean , he was showing up uh some {disfmarker} something on noisy speech ,

**Professor C:** Yeah .

**PhD A:** some improvement on the noisy speech .

**PhD D:** Mm - hmm .

**PhD A:** Some small vocabulary tasks .

**Professor C:** Uh .

**PhD A:** So it was on PLP derived cepstral coefficients .

**Professor C:** Yeah , but again {disfmarker} You could argue that th that 's exactly what the neural network does .

**PhD A:** Mmm .

**Professor C:** So n neural network uh , is in some sense equivalent to computing , you know , higher - order moments of what you {disfmarker}

**PhD A:** trying to f to Moments , yeah . Yeah .

**Professor C:** yeah . So . I mean , it doesn't do it very specifically ,

**PhD D:** Mm - hmm .

**Professor C:** and pretty {disfmarker} you know . But .

**PhD A:** Yep .

**Professor C:** Uh , anything on your end you want to talk about ? Uh .

**Grad G:** Um , nothing I wanna really talk about . I can {disfmarker} I can just uh , um , share a little bit {disfmarker} Sunil hasn't {disfmarker} hasn't heard about uh , what I 've been doing .

**Professor C:** Yeah .

**Grad G:** Um , so , um , I told you I was {disfmarker} I was {disfmarker} I was getting prepared to take this qualifier exam . So basically that 's just , um , trying to propose um , uh , your next your {disfmarker} your following years of {disfmarker} of your PHD work , trying {disfmarker} trying to find a project to {disfmarker} to define and {disfmarker} and to work on . So , I 've been , uh , looking into , um , doing something about r uh , speech recognition using acoustic events . So , um , the idea is you have all these {disfmarker} these different events , for example voicing , nasality , R - coloring , you know burst or noise , uh , frication , that kinda stuff , um , building robust um , primary detectors for these acoustic events , and using the outputs of these robust detectors to do speech recognition . Um , and , um , these {disfmarker} these primary detectors , um , will be , uh , inspired by , you know , multi - band techniques , um , doing things , um , similar to Larry Saul 's work on , uh , graphical models to {disfmarker} to detect these {disfmarker} these , uh , acoustic events . And , um , so I {disfmarker} I been {disfmarker} I been thinking about that and some of the issues that I 've been running into are , um , exactly what {disfmarker} what kind of acoustic events I need , what {disfmarker} um , what acoustic events will provide a {disfmarker} a good enough coverage to {disfmarker} in order to do the later recognition steps . And , also , um , once I decide a set of acoustic events , um , h how do I {disfmarker} how do I get labels ? Training data for {disfmarker} for these acoustic events . And , then later on down the line , I can start playing with the {disfmarker} the models themselves , the {disfmarker} the primary detectors . Um , so , um , I kinda see {disfmarker} like , after {disfmarker} after building the primary detectors I see um , myself taking the outputs and feeding them in , sorta tandem style into {disfmarker} into a um , Gaussian mixtures HMM back - end , um , and doing recognition . Um . So , that 's {disfmarker} that 's just generally what I 've been looking at .

**PhD A:** Yeah .

**Grad G:** Um ,

**Professor C:** By {disfmarker} by the way , uh , the voiced - unvoiced version of that for instance could tie right in to what Carmen was looking at .

**Grad G:** Yeah .

**Professor C:** So ,

**PhD D:** Mm - hmm .

**Professor C:** you know , um , if you {disfmarker} if a multi - band approach was helpful as {disfmarker} as I think it is , it seems to be helpful for determining voiced - unvoiced ,

**Grad G:** Mm - hmm .

**Professor C:** that one might be another thing .

**PhD B:** Mm - hmm .

**Grad G:** Yeah . Yeah . Um , were {disfmarker} were you gonna say something ?

**PhD F:** Mmm .

**Grad G:** Oh . It looked {disfmarker} OK , never mind . Um , yeah . And so , this {disfmarker} this past week um , I 've been uh , looking a little bit into uh , TRAPS um , and doing {disfmarker} doing TRAPS on {disfmarker} on these e events too , just , um , seeing {disfmarker} seeing if that 's possible . Uh , and um , other than that , uh , I was kicked out of I - house for living there for four years .

**Professor C:** Oh no . So you live in a cardboard box in the street now

**Grad G:** Yeah .

**Professor C:** or , no ?

**Grad G:** Uh , well , s s som something like that .

**Professor C:** Yeah .

**Grad G:** In Albany , yeah . Yeah . And uh . Yep . That 's it .

**Professor C:** Suni - i d ' you v did uh {disfmarker} did you find a place ?

**PhD A:** Uh , no

**Professor C:** Is that out of the way ?

**PhD A:** not yet . Uh , yesterday I called up a lady who ha who will have a vacant room from May thirtieth and she said she 's interviewing two more people . So . And she would get back to me on Monday . So that 's {disfmarker} that 's only thing I have and Diane has a few more houses . She 's going to take some pictures and send me after I go back . So it 's {disfmarker} that 's {disfmarker}

**Professor C:** OK .

**PhD F:** Oh . So you 're not down here permanently yet ?

**PhD A:** No . I 'm going back to OGI today .

**PhD F:** Ah ! Oh , OK .

**Grad G:** Oh .

**Professor C:** OK . And then , you 're coming back uh {disfmarker}

**PhD A:** Uh , i I mean , I {disfmarker} I p I plan to be here on thirty - first .

**Professor C:** Thirty - first ,

**PhD A:** Yeah , well if there 's a house available or place to {disfmarker}

**Professor C:** OK .

**Grad G:** Thirty - first .

**Professor C:** Well , I mean i i if {disfmarker} if {disfmarker}

**PhD A:** Yeah , I hope .

**Professor C:** They 're available , and they 'll be able to get you something , so worst comes to worst we 'll put you up in a hotel for {disfmarker} for {disfmarker} for a while

**PhD A:** Yeah . So , in that case , I 'm going to be here on thirty - first definitely .

**Professor C:** until you {disfmarker} OK .

**Grad E:** You know , if you 're in a desperate situation and you need a place to stay , you could stay with me for a while . I 've got a spare bedroom right now .

**PhD A:** Oh . OK . Thanks . That sure is nice of you . So , it may be he needs more than me .

**Grad G:** Oh r oh . Oh no , no . My {disfmarker} my cardboard box is actually a nice spacious two bedroom apartment .

**Professor C:** So a two bedroom cardboard box . Th - that 's great .

**PhD A:** Yeah . Yeah . {vocalsound} Yeah .

**Professor C:** Thanks Dave .

**Grad G:** yeah

**PhD A:** Yeah .

**Professor C:** Um ,

**PhD A:** Yeah .

**Professor C:** Do y wanna say anything about {disfmarker} You {disfmarker} you actually been {disfmarker} Uh , last week you were doing this stuff with Pierre , you were {disfmarker} you were mentioning . Is that {disfmarker} that something worth talking about , or {disfmarker} ?

**Grad E:** Um , it 's {disfmarker} Well , um , it {disfmarker} I don't think it directly relates . Um , well , so , I was helping a speech researcher named Pierre Divenyi and he 's int He wanted to um , look at um , how people respond to formant changes , I think . Um . So he {disfmarker} he created a lot of synthetic audio files of vowel - to - vowel transitions , and then he wanted a psycho - acoustic um , spectrum . And he wanted to look at um , how the energy is moving {pause} over time in that spectrum and compare that to the {disfmarker} to the listener tests . And , um . So , I gave him a PLP spectrum . And {disfmarker} to um {disfmarker} he {disfmarker} he t wanted to track the peaks so he could look at how they 're moving . So I took the um , PLP LPC coefficients and um , I found the roots . This was something that Stephane suggested . I found the roots of the um , LPC polynomial to , um , track the peaks in the , um , PLP LPC spectra .

**PhD A:** well there is aligned spectral pairs , is like the {disfmarker} the {disfmarker} Is that the aligned s

**Professor C:** It 's a r root LPC , uh , of some sort .

**PhD A:** Oh , no .

**PhD D:** Mm - hmm .

**PhD A:** So you just {disfmarker}

**Professor C:** Yeah .

**PhD A:** instead of the log you took the root square , I mean cubic root or something . What di w I didn't get that .

**Professor C:** No , no . It 's {disfmarker} it 's {disfmarker} it 's taking the {disfmarker} finding the roots of the LPC polynomial .

**PhD A:** Polynomial . Yeah . Is that the line spectral {disfmarker}

**Professor C:** So it 's like line spectral pairs .

**PhD A:** Oh , it 's like line sp

**Professor C:** Except I think what they call line spectral pairs they push it towards the unit circle , don't they ,

**PhD A:** Yeah , yeah , yeah , yeah .

**Professor C:** to sort of ? But it {disfmarker} But uh , you know . But what we 'd used to do w when I did synthesis at National Semiconductor twenty years ago , the technique we were playing with initially was {disfmarker} was taking the LPC polynomial and {disfmarker} and uh , finding the roots . It wasn't PLP cuz Hynek hadn't invented it yet , but it was just LPC , and uh , we found the roots of the polynomial , And th When you do that , sometimes they 're f they 're what most people call formants , sometimes they 're not .

**PhD A:** Mmm .

**Professor C:** So it 's {disfmarker} it 's {disfmarker} it 's a little ,

**PhD D:** Hmm .

**Professor C:** uh {disfmarker} Formant tracking with it can be a little tricky cuz you get these funny {vocalsound} values in {disfmarker} in real speech ,

**PhD F:** So you just {disfmarker} You typically just get a few roots ?

**Professor C:** but .

**PhD F:** You know , two or three ,

**Professor C:** Well you get these complex pairs .

**PhD F:** something like that ?

**Professor C:** And it depends on the order that you 're doing , but .

**PhD D:** Mm - hmm .

**Grad E:** Right . So , um , if {disfmarker} @ @ {comment} Every root that 's {disfmarker} Since it 's a real signal , the LPC polynomial 's gonna have real coefficients . So I think that means that every root that is not a real root {comment} is gonna be a c complex pair ,

**PhD F:** Mm - hmm .

**Grad E:** um , of a complex value and its conjugate . Um . So for each {disfmarker} And if you look at that on the unit circle , um , one of these {disfmarker} one of the members of the pair will be a positive frequency , one will be a negative frequency , I think . So I just {disfmarker} So , um , f for the {disfmarker} I 'm using an eighth - order polynomial and I 'll get three or four of these pairs

**Professor C:** Yeah .

**PhD A:** Hmm .

**Grad E:** which give me s which gives me three or four peak positions .

**Professor C:** This is from synthetic speech , or {disfmarker} ?

**Grad E:** It 's {disfmarker} Right . Yeah .

**Professor C:** Yeah . So if it 's from synthetic speech then maybe it 'll be cleaner . I mean for real speech in real {disfmarker} then what you end up having is , like I say , funny little things that are {disfmarker} don't exactly fit your notion of formants all that well .

**PhD F:** How did {disfmarker}

**Professor C:** But {disfmarker} but mostly they are .

**PhD D:** But

**Professor C:** Mostly they do .

**PhD D:** Yeah .

**Grad E:** Mmm ,

**Professor C:** And {disfmarker} and what {disfmarker} I mean in {disfmarker} in what we were doing , which was not so much looking at things , it was OK

**PhD D:** I {disfmarker}

**Professor C:** because it was just a question of quantization . Uh , we were just you know , storing {disfmarker} It was {disfmarker} We were doing , uh , stored speech , uh , quantization .

**PhD D:** Mm - hmm .

**Professor C:** But {disfmarker} but uh , in your case um , you know {disfmarker}

**PhD D:** Actually you have peaks that are not at the formant 's positions , but they are lower in energy

**Grad E:** But {disfmarker} there 's some of that , yes .

**PhD D:** and {disfmarker} Well they are much lower .

**PhD F:** If this is synthetic speech can't you just get the formants directly ? I mean h how is the speech created ?

**Grad E:** It was created from a synthesizer , and um {disfmarker}

**PhD F:** Wasn't a formant synthesizer was it ?

**Professor C:** I bet it {disfmarker} it might have {disfmarker} may have been

**Grad E:** I {disfmarker} d d this {disfmarker}

**Professor C:** but maybe he didn't have control over it or something ?

**Grad E:** In {disfmarker} in fact w we {disfmarker} we could get , um , formant frequencies out of the synthesizer , as well . And , um , w one thing that the , um , LPC approach will hopefully give me in addition , um , is that I {disfmarker} I might be able to find the b the bandwidths of these humps as well . Um , Stephane suggested looking at each complex pair as a {disfmarker} like a se second - order IIR filter .

**Professor C:** Yeah .

**Grad E:** Um , but I don't think there 's a g a really good reason not to um , get the formant frequencies from the synthesizer instead . Except that you don't have the psycho - acoustic modeling in that .

**Professor C:** Yeah , so the actual {disfmarker} So you 're not getting the actual formants per se . You 're getting the {disfmarker} Again , you 're getting sort of the , uh {disfmarker}

**PhD D:** Mm - hmm .

**Professor C:** You 're getting something that is {disfmarker} is uh , af strongly affected by the PLP model . And so it 's more psycho - acoustic . So it 's a little {disfmarker} It 's {disfmarker} It 's {disfmarker} It 's sort of {disfmarker} sort of a different thing .

**PhD F:** Oh , I see . That 's sort of the point .

**Professor C:** But {disfmarker} Yeah . i Ordinarily , in a formant synthesizer , the bandwidths as well as the ban uh , formant centers are {disfmarker}

**PhD F:** Yeah .

**Professor C:** I mean , that 's {disfmarker} Somewhere in the synthesizer that was put in , as {disfmarker} as what you {disfmarker}

**Grad E:** Mm - hmm .

**Professor C:** But {disfmarker} but yeah , you view each complex pair as essentially a second - order section , which has , uh , band center and band width , and um , um {disfmarker} But . Yeah . O K . So , uh , yeah , you 're going back today and then back in a week I guess ,

**PhD A:** Yeah .

**Professor C:** and . Yeah . Great ! Well , welcome .

**PhD A:** Thanks .

**PhD F:** I guess we should do digits quickly .

**Professor C:** Oh yeah , digits .

**PhD D:** Mmm .

**Professor C:** I almost forgot that .

**PhD B:** Digits .

**Professor C:** I almost forgot our daily digits .

**PhD F:** You wanna go ahead ?

**Professor C:** Sure .

**PhD F:** OK .
