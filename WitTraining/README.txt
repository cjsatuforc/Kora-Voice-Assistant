---Brief Summary of Instructions---
1) All changes should be made in trainWit.py.
2) To create a new training phrase, use the TrainingPhrase class.
3) When you construct a training phrase, provide the constructor with the name of the intent (e.g. 'rotate') by using the Intents class and the string that is your phrase.
4) You can tag entities in your phrase by using the Entity class.
   For example: 'save this as ' + Entity('myFile', EntityTypes.Filename)
   would be a hypothetical phrase for training the Save As command if the
   Filename member was actually in the EntityTypes class.
5) Add all of your training phrases to the generateTrainingPhrases function.
6) Make sure to provide your GitHub credentials via the getLoginCreds function.
7) Run trainWit.py with python 3 to train with whatever is in the generateTrainingPhrases function.

---Instructions---
All changes to add new training data should be made in trainWit.py.
When you have added everything you want, just run "python3 trainWit.py".
See the getLoginCreds function to see how to provide your GitHub login credentials so it can login to Wit.ai.
You can change how the function gets your credentials as long as the returned dictionary has the same format.
To training phrases are generated in the generateTrainingPhrases function.
There are two ways to add phrases for training Wit on to this function.
The first is to enter the phrase manually which you can see at the bottom of the function with TrainingPhrase(Intents.save, 'save').
The other way is to randomly generate phrases with another function then just loop through the phrases that were generated and yield each of those individually which is what is happening with the line that uses RandomRotate.
To actually construct a training phrase, you need to use the TrainingPhrase class.
The constructor for this class takes two arguments.
The first argument is the intent of the phrase.
The second argument is the string that constitutes the phrase.
If there are any entities in your string, use the Entity class which takes the string to tag and the type of entity it is.
For example, let's say I was training a Save As command which had an entity called 'filename'.
To create the training phrase I would want something like: TrainingPhrase(Intents.SaveAs, 'save this as' + Entity('myFileName', EntityTypes.Filename)).
Note that this requires you to make sure that your entity's name is in the EntityTypes class. 
You should use intents from the Intents class, you can add your own if you are using a new intent.
Just to be safe, you should create a new intent in Wit if you are adding it to the trainer before using the trainer to train that new intent.
It should be able to create new intents on it's own, but it's safer to create the intent manually before traiing it.

