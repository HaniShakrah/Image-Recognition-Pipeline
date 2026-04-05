S3_BUCKET = "cs643-njit-project1"         

SQS_QUEUE_NAME = "t19.fifo"  

AWS_REGION = "us-east-1"

CAR_CONFIDENCE_THRESHOLD  = 80.00000000000000
TEXT_CONFIDENCE_THRESHOLD = 80.00000000000000

POLL_WAIT_SECONDS = 20   # SQS long-poll duration (max 20)
VISIBILITY_TIMEOUT = 30  # seconds to hide message while processing

QUEUE_END = "END"

OUTPUT_FILE = "results.txt"
