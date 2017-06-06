# ReBBR: Reproducing BBR Performance on Lossy Networks

[![link_to_blog](https://img.shields.io/badge/blogpost-5%20June%202017-orange.svg)](https://reproducingnetworkresearch.wordpress.com/2017/06/05/rebbr/)
[![GitPitch](https://gitpitch.com/assets/badge.svg)](https://gitpitch.com/jervisfm/rebbr/dev?grs=github&t=white)
[![link_to_paper](https://img.shields.io/badge/original-paper-blue.svg)](https://research.google.com/pubs/pub45646.html)

## Introduction
This is the code that was used to reproduce the BBR results described [in our blog post](https://reproducingnetworkresearch.wordpress.com/2017/06/05/rebbr/). Specifically, we target the BBR result that BBR significantly outperforms CUBIC over networks with non-negligable loss rates, summarized in Figure 8 of the [original paper](https://research.google.com/pubs/pub45646.html).


## Step-by-step Instructions
In order to reproduce our results, you can follow the step by step instructions that follow.
As an overview, we will be creating a virtual machine, installing a Linux kernel that includes BBR congestion control, installing [Mahimahi](http://mahimahi.mit.edu/) (a network emulator), and using it to run a series of experiments. This whole process to replicate our results should take about 8.5 hours.

We provide instructions for running this experiment on Google Cloud, but you could follow
the same instructions on any Ubuntu 16.04 machine, on a local VM for instance.

### Setup a Google Compute Engine Instance
To perform these steps, you will need a Google Cloud account with Billing enabled.
Visit http://cloud.google.com and create a new project to run the experiment in.

1. Go to your [Google Cloud Console](https://console.cloud.google.com/) and click on `Compute Engine > Images`.
2. Select the `ubuntu-1604` image, and select it by ticking the checkbox next to the image.
3. Click on `Create Instance` in the toolbar at the top of the screen.
4. Select an instance name (e.g. `rebbr`).
5. Choose which zone you want to launch the instance in (e.g. `us-west1-c`).
6. Select `2 vCPUs` as the machine type (specifically, the `n1-standard-2`).
7. Check the `Allow HTTP traffic` checkbox under the Firewall settings. This will be used to view the results of the experiments.
8. Click `Create` to create your instance. All other settings can be left at their default values.

Now, you will be brought back to the Google Cloud Console, and can connect to your VM using SSH.

### Installing and Running Experiments
Next, we will install the necessary dependencies and prerequisites on our VM.

1. SSH into the VM using the method of your choice (e.g. through the Google Cloud Console)
2. Clone the repository into the `~/bbr` folder.
    ```sh
    git clone https://github.com/jervisfm/rebbr.git bbr
    ```
3. Upgrade the Linux kernel to v4.11.1
    ```sh
    cd bbr && ./vm_upgrade_kernel.sh
    ```
4. Restart the VM by using the commandline by running:
    ```sh
    sudo reboot
    ```
5. Wait for the instance to restart, and reconnect to it via SSH.
6. Verify that the kernel upgrade worked by running `uname -sr`. This should output `Linux 4.11.1-041101-generic`. If not, the kernel was not updated. You may need to rerun step 3 and reboot again.
7. To install all dependencies and run all experiments, run `cd bbr && ./run_all.sh`. This will take approximately 8.5 hours. During this run, you will see some logging output printed to the console, which allows you to monitor which experiment is being run.
8. Finally, to view the experiment results, identify your VM-instance's _external_ IP address in the Google Cloud Console (e.g. 104.199.120.104). You will be able to browse the figures by opening your browers and navigating to `http://<external-ip>/figures/`. Note that this external ip is not static, so if you run the experiments again later, you will need to check for the current external ip address.

You can also identify your VM public IP address by running:
```
$ dig +short myip.opendns.com @resolver1.opendns.com
```

Don't forget to shut down your Google Cloud instance when you are done!

## Experiment Results

### Figure 8
This is our reproduction of figure 8 from original paper that looks at how CUBIC and BBR perform
at varying loss rates.

![rebbr_figure8](mahimahi/figures/figure8.png "ReBBR Figure 8")

### Experiment 1
Experiment 1 looks at BBR and CUBIC performance over loss links acrossing various link speeds.

![rebbr_experiment1](mahimahi/figures/experiment1.png "ReBBR Experiment 1")

### Experiment 2
Experiment 2 looks at how various Congestion Control Algorithms found in linux kernel behave
over various loss rates.

![rebbr_experiment2](mahimahi/figures/experiment2.png "ReBBR Experiment 2")

### Experiment 3
Experiment 3 looks at impact of RTT on performance of CUBIC and BBR over various loss rates.

![rebbr_experiment3](mahimahi/figures/experiment3.png "ReBBR Experiment 3")


### Experiment 4
Experiment 4 compares BBR and CUBIC performance over a cellular link trace with varying
RTT and bandwidth captured from the Verizon network.

![rebbr_experiment4](mahimahi/figures/experiment4.png "ReBBR Experiment 4")
