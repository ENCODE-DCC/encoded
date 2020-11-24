Organization deployment configuration and build files
=====================================================
    When bin/deploy is run user_data is sent to AWS.  The user_data defines the type of deployment, 
    i.e. Demo, es cluster, frontend, etc.  The user_data is compiled in two stages.  The first 
    stage creates an Assembled Template.  By default the template is in memory but a bin/deploy
    argument exists that allows the assembled template to be saved and used later.  The second stage 
    adds Run Variables to the Assembled Template.  Then it can be sent as user_data to AWS to create
    an instance.

# Summary of cloud-config directory structure

#### Templates are assembled with ./template-parts
    # Standard Templates
    Demo/QA Demo                : app-es-pg-template.yml
    Cluster Frontend            : app-pg-template.yml
    Cluster Elasticsearch       : es-nodes-template.yml
    
    # Non Standard Templates
    Instance with remote pg     : app-es-template.yml
    Instance with remote pg/es  : app-template.yml

    Open one of the templates above to compare with ./template-parts.  Each variable '%(varname)s' 
    in the template has a matching file in ./template-parts.  Next is a way to view and save
    assembled templates.

    We can save Assembled Templates with the --save-configure bin/deploy argument.  It will 
    automaticallly determine which template to used based on input arguments.

    $ bin/deploy --save-config-name 20200430

    ### Output
    Created assembeled template
           ./cloud-config/assembled-templates/20200430-app-es-pg.yml
    Deploy with
           $ bin/deploy --use-prebuilt-config 20200430-app-es-pg
    Diff with on the fly assembly.  Does not deploy
           $ bin/deploy --use-prebuilt-config 20200430-app-es-pg --diff-configs
    ###


#### Directories:
    template-parts              : Pieces of the templates
    run-scripts                 : Install scripts runcmd_* template parts
    configs                     : Configuration files used in run-scripts, like apache, java, es
    assembled-templates         : Saved.  These still contains Run Varialbes

#### Helper Script
    create-ami.py               : Create amis from deployed --ami-build in AWS

#### Run_Variables
    * Run variables are in /etc/environment file on the instance.  
    * They are used in the run-scripts to configure the system and application builds
    * /etc/environment is loaded into login/ssh sessions so you can echo them on the instance.
    * The file will contain dupicate entries when deploying from an AMI.  Last ones are used.
    
    View them locally with --dry-run along with other info.  Does not deploy
    $ bin/deploy --dry-run

    Add options like --test, --release-candidate, or --candidate to see the differences in run vars.
    The ROLE should change along with other variables like ENCD_INDEX_PRIMARY, ENCD_INDEX_VIS,
    ENCD_INDEX_REGION.  The env vars are prefixed with ENCD_ as to not conflict with other env vars.
