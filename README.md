# Remote client for workflow analysis

## Install

```
$git clone git@github.com:Deepomatic/deepomatic-workflows-remote.git
$cd deepomatic-workflows-remote.git
$pip install .
```

## Setup

Before running your first command you must be added to the `dp-customers-unit-t` gcp project.
Then, create a secret auth file for your service account:

```
$gcloud iam service-accounts keys create wf-secret.json --iam-account=<your service account>
```

The naming convention `wf-secret.json` must be respected. The file must be place in the same directory you
are running the command.


## Usage

`wf_client remote --project /path/to/project --api-key <vulcain organization key> --entry <entry_name:entry_value> --payload payload.json`

Inside payload.json:
```
{
    "task_group_name": "<name of the task group you want to execute>",
    "work_order_types": [] # optionnal,
    "state": {} # optionnal,
    "analysis_metadata": {} # optionnal,
    "wo_metadata": {} # optionnal
}
```

## FAQ

### Service Unavailable

Maybe a timeout. If models are note loaded on our side, the remote workflow
will timeout before the the models are online, leading to `Service Unavailable`.
You can lauch again the command, if it was just about the models, it should work.
