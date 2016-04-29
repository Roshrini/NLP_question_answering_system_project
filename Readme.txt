Instructions to run our project on cade:

1) We are using Python3.5 and NLTK package
2) Please run following command and install additional packages.
/usr/local/stow/python/amd64_linux26/python-3.5.0/bin/python3 -m nltk.downloader -d /home/$USERNAME/nltk_data all

Replace $USERNAME with your cade username.

Open our folder. Go to question-answers folder where there are other files.

3) /usr/local/stow/python/amd64_linux26/python-3.5.0/bin/python3 question_answers.py ./developset/input.txt > Response.answer

After running above command, Response.answer file will be generated. This is our output file.

You can calculate accuracy on this file. We got accuracy as 25.89% on developset.