# Introduction

This is a project to reproduce Google BBR network performance results over lossy network links.

Link to paper: https://research.google.com/pubs/pub45646.html

## Collaborators
* Jervis
* Luke

# Figure To Reproduce

The figure we are interested in reproducing is Figure 8 that shows BBR performance over lossy links
when compared to [CUBIC](https://en.wikipedia.org/wiki/CUBIC_TCP). This figure is shown below:


![bbr_figure8](bbr_fig8.png "BBR Figure 8")


# Setup

The highlevel approach is:

1) Setup a Virtual Machine with BBR enabled.
2) Install Mahimahi Emulations tools
3) Use LinkShell and DelayShells to simulate differing amount of losses.


## Step 1: VM Setup

For this part, we'll follow the guide published by Google here: https://github.com/google/bbr/blob/master/Documentation/bbr-quick-start.md

### Running Appendix Notes:

Executing vanilla gcloud compute after install Gcloud SDK command results in an error:
```
gcloud compute \
>   instances create "bbrtest1" \
>   --project ${PROJECT} --zone ${ZONE} \
>   --machine-type "n1-standard-8" \
>   --network "default" \
>   --maintenance-policy "MIGRATE" \
>   --boot-disk-type "pd-standard" \
>   --boot-disk-device-name "bbrtest1" \
>   --image "/ubuntu-os-cloud/ubuntu-1604-xenial-v20160922" \
>   --boot-disk-size "20" \
>   --scopes default="https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring.write","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly"
WARNING: You have selected a disk size of under [200GB]. This may result in poor I/O performance. For more information, see: https://developers.google.com/compute/docs/disks#pdperformance.
WARNING: Flag format --scopes [ACCOUNT=]SCOPE, [[ACCOUNT=]SCOPE, ...] is deprecated and will be removed 24th Jan 2018. Use --scopes SCOPE[, SCOPE...] --service-account ACCOUNT instead.
ERROR: (gcloud.compute.instances.create) Could not fetch resource:
 - Invalid value for field 'resource.disks[0].initializeParams.sourceImage': 'https://www.googleapis.com/compute/v1/projects/make-tcp-fast/global/images//ubuntu-os-cloud/ubuntu-1604-xenial-v20160922'. The URL is malformed.
```

From docs here: https://cloud.google.com/sdk/gcloud/reference/compute/instances/create, it says we can find available names with:

```
$ gcloud compute images list
```

Available ubuntu images are:
```
ubuntu-1404-trusty-v20170505                      ubuntu-os-cloud    ubuntu-1404-lts                       READY
ubuntu-1604-xenial-v20170502                      ubuntu-os-cloud    ubuntu-1604-lts                       READY
ubuntu-1610-yakkety-v20170502                     ubuntu-os-cloud    ubuntu-1610                           READY
ubuntu-1704-zesty-v20170413                       ubuntu-os-cloud    ubuntu-1704                           READY
```

However, even using ubuntu-1604-xenial-v20170502 still errors out.

Ah, I tried running the example command on the doc and even that errors out still:
```
gcloud compute instances create example-instance \
      --image-family rhel-7 --image-project rhel-cloud \
      --zone us-central1-a
- Failed to find project google-bbr
```

So, it looks like project setup failed.

Ah, the problem looks to be a difference between project ID and project name. Create a project on the web (http://console.google.com)
and list available project like so:

```
$ gcloud projects list
PROJECT_ID            NAME        PROJECT_NUMBER
extreme-braid-167301  google-bbr  142604555723
```

Then Update your local project config:
```
$ gcloud config set project extreme-braid-167301
```

This is a bit wierd since the project ids are machine generated and don't have memorable names.

Next up, you need to enable Billing to do actual sort of action. You can use the Education credit available here: https://goo.gl/gcpedu/omXu3b as
a Billing source. 

With that, can create an Instance following GCloud example command.