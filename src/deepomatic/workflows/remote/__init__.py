from contextlib import contextmanager
import json
import os
import tempfile
import zipfile

import click
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
import requests  # type: ignore


class RemoteWorkflowClient:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        credentials = service_account.IDTokenCredentials.from_service_account_file("wf-secret.json", target_audience=self.api_url)
        self.http = AuthorizedSession(credentials)

    def remote_workflow(self, files, data):
        response = self.http.post(f"{self.api_url}", files=files, data=data, headers={"X-API-KEY": self.api_key})
        return response


def _workflow_inputs(inputs):
    return {input_.split(":")[0]: open(input_.split(":")[1], "rb") for input_ in inputs}


@contextmanager
def _workflow_archive(project_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        current_pwd = os.getcwd()
        archive_name = os.path.join(tmpdir, "workflow_remote.zip")
        try:
            os.chdir(project_path)
            with zipfile.ZipFile(archive_name, "w") as zf:
                for dirname, subdirs, files in os.walk("./"):
                    zf.write(dirname)
                    for filename in files:
                        zf.write(os.path.join(dirname, filename))
        finally:
            os.chdir(current_pwd)

        with open(archive_name, "rb") as archive:
            yield archive


@click.command(name="remote")
@click.option(
    "-e",
    "--entry",
    "inputs",
    nargs=1,
    multiple=True,
    help="Entry, in the format entry_name:entry_value (e.g input_name:./image.jpeg)",
)
@click.option(
    "-p",
    "--project",
    "project",
    nargs=1,
    type=click.Path(),
    default="",
    help="Path to project.",
)
@click.option(
    "--payload",
    "payload",
    nargs=1,
    type=click.Path(),
    default="",
    help="Json file with the payload to send.",
)
@click.option(
    "--api-key",
    "vulcain_api_key",
    nargs=1,
    required=True,
    help="Remote api key.",
)
def command_remote(inputs, project, payload, vulcain_api_key):
    # So far, for service account to work:
    # gcloud iam service-accounts keys create wf-secret.json --iam-account=952180803176-compute@developer.gserviceaccount.com

    client = RemoteWorkflowClient(api_url="https://workflow-server-zi6eerhjeq-uc.a.run.app", api_key=vulcain_api_key)

    with open(payload, "r") as payload_:
        body = json.load(payload_)

    with _workflow_archive(project) as workflow_archive:
        files = {"workflow_zip": workflow_archive, **_workflow_inputs(inputs)}

        response = client.remote_workflow(files=files, data=body)

        try:
            result = response.json()
            if response.status_code == 200:
                print(json.dumps(json.loads(response.content), indent=2))
            else:
                print(f"Error code {response.status_code}: {result['error']}")
                # FIXME: Add result['logs'] when present in response
                print(f"{result['backtrace']}")
        except json.JSONDecodeError:
            print(response.text)
        except Exception as err:
            print(err)


@click.group()
def cli() -> None:
    """
    This is the workflow v2 client
    """


cli.add_command(command_remote)
