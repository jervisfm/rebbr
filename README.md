# ReBBR: Reproducing BBR Performance on Lossy Networks

[![link_to_blog](https://img.shields.io/badge/blog-3%20June%202017-green.svg)](https://reproducingnetworkresearch.wordpress.com/)
[![link_to_paper](https://img.shields.io/badge/original-paper-blue.svg)](https://research.google.com/pubs/pub45646.html)

## Introduction
This is the code that was used to reproduce the BBR results described [in our blog post](https://reproducingnetworkresearch.wordpress.com/). Specifically, we target the BBR result that BBR significantly outperforms CUBIC over networks with non-negligable loss rates, summarized in Figure 8 of the [original paper](https://research.google.com/pubs/pub45646.html).


## Step-by-step Instructions
In order to reproduce our results, you can follow the step by step instructions that follow.
As an overview, we will be creating a virtual machine, installing a Linux kernel that includes BBR congestion control, installing [Mahimahi](http://mahimahi.mit.edu/) (a network emulator), and using it to run a series of experiments. This whole process should take about **TODO** hours.

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
    git clone https://github.com/jervisfm/GoogleBBR-Replicating-Fig8.git bbr
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
7. Install Mahimahi and other Python dependencies by running:
    ```sh
    cd bbr/mahimahi && ./init_deps.sh
    ```
8. To run all experiments, run `./run_experiments_headless.sh`. This will take approximately **TODO** hours. During this run, you will see some logging output printed to the console, which allows you to monitor which experiment is being run.
9. Finally, to view the experiment results, identify your VM-instance's _external_ IP address in the Google Cloud Console (e.g. 104.199.120.104). You will be able to browse the figures by opening your browers and navigating to `http://<external-ip>/bbr/mahimahi/data/`. Note that this external ip is not static, so if you run the experiments again later, you will need to check for the current external ip address.

Don't forget to shut down your Google Cloud instance when you are done!
