# CS 643 Cloud Computing — Project 1
## AWS Image Recognition Pipeline

## Link to Demo Video: https://www.youtube.com/watch?v=frrI6syw83Y

## Setup Steps

**Step 1 — Download Credentials**
- Download the `.pem` key from **Learner Lab → AWS Details** and save it in your project folder
- Save your `aws_access_key_id`, `aws_secret_access_key`, and `aws_session_token` from the same page for later use

---

**Step 2 — Launch EC2 Instances in AWS Console**   

Repeate the below twice to create "Instance A" and "Instance B"
- Go to **EC2 → Launch Instance**
- Select **Amazon Linux AMI**
- Key pair: select **vockey**
- Under Network Settings:
  - Set source to **My IP**
  - Allow **SSH**, **HTTP**, and **HTTPS**
- Launch the instance

---

**Step 3 — Set Up Remote Connection in VS Code**
- Press `Ctrl+Shift+P` and select **Remote-SSH: Connect to Host...**
- Click **Add New SSH Host**
- Enter the SSH command with your instance's public IP:

```
ssh -i "C:\path\to\labsuser.pem" ec2-user@<PUBLIC_IP>
```

- Select where to save the SSH config file
- The host will be added to your Remote Hosts list

---

**Step 4 — Open the Remote Host**
- Go to **Remote Explorer** in the VS Code sidebar
- Click **Open in New Window** next to your instance
- Open the `ec2-user` home folder

---

**Step 5 — Copy Files to EC2 (Run from Local Terminal)**

Run these commands from your **local** VS Code terminal (not the remote one):

Copy `object_recognition.py` and `config.py` into **Instance A**
```bash
scp "C:\path\to\object_recognition.py" ec2-user@<PUBLIC_IP>:~/
scp "C:\path\to\config.py" ec2-user@<PUBLIC_IP>:~/
```
Copy `text_detection.py` and `config.py` into **Instance B**

```bash
scp "C:\path\to\text_detection.py" ec2-user@<PUBLIC_IP>:~/
scp "C:\path\to\config.py" ec2-user@<PUBLIC_IP>:~/
```

> Use the appropriate IP for each instance.

---

**Step 6 — Install Dependencies (Run on Each EC2 Instance)**

In the remote VS Code terminal:

```bash
sudo yum install python3-pip -y
pip3 install boto3
```

---

**Step 7 — Configure AWS Credentials (Run on Each EC2 Instance)**

```bash
mkdir -p ~/.aws
touch ~/.aws/credentials
code ~/.aws/credentials
```

Paste the `aws_access_key_id`, `aws_secret_access_key`, and `aws_session_token` from **Step 1** into the file

```
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
aws_session_token = YOUR_TOKEN
```

> **Note:** These credentials expire at the end of each Learner Lab session. Update this file each time you start a new session.

---

**Step 8 — Run the Pipeline**

- **Note:** The code handles the case where the object_recognition script runs first and the case where the text_detection script starts first 

Start one instance:

Instance A:
```bash
python3 -W ignore object_recognition.py
```

Then start the other instance in a separate terminal window:

Instance B:
```bash
python3 -W ignore text_detection.py
```

The two instances will run in parallel. Instance A detects cars and sends image indexes to SQS. Instance B polls the queue and performs text detection on those images.

Again, you can start Instance A before Instance B, or vice versa

---

**Step 9 — Check Output**

When Instance B finishes, the results are written to `output.txt` in the home directory:



The file lists all images that contain both a car and text, along with the detected text for each image.

---

## Notes
- Terminate your instances after you are done to avoid charges
- The SQS queue is manually created in the script, according to the name specified in config.py
