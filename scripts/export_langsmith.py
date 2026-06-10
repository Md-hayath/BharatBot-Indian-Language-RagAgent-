from langsmith import Client

client = Client()

if __name__ == "__main__":
    runs = client.list_runs(project_name="bharatbot", limit=10)
    for run in runs:
        print(f"\nID     : {run.id}")
        print(f"Status : {run.status}")
        print(f"Input  : {str(run.inputs)[:150]}")
        print(f"Output : {str(run.outputs)[:150]}")