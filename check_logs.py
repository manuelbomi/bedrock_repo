"""Check runtime logs for agent_with_memory_2"""
import boto3
from datetime import datetime, timedelta

region = "us-east-1"
log_group = "/aws/bedrock-agentcore/runtimes/agent_with_memory_2-aq9shtARJa-DEFAULT"

logs_client = boto3.client('logs', region_name=region)

try:
    # Get the most recent log streams
    response = logs_client.describe_log_streams(
        logGroupName=log_group,
        orderBy='LastEventTime',
        descending=True,
        limit=5
    )

    print(f"Found {len(response['logStreams'])} recent log streams\n")

    # Get logs from each stream
    for stream in response['logStreams']:
        stream_name = stream['logStreamName']
        print(f"\n{'='*80}")
        print(f"Log Stream: {stream_name}")
        print(f"Last Event: {datetime.fromtimestamp(stream.get('lastEventTimestamp', 0) / 1000)}")
        print(f"{'='*80}\n")

        # Get log events
        events_response = logs_client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            startFromHead=False,
            limit=100
        )

        for event in events_response['events']:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message']
            print(f"[{timestamp}] {message}")

except Exception as e:
    print(f"Error getting logs: {e}")
    import traceback
    traceback.print_exc()
