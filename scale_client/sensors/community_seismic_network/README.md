Community Seismic Network integration for SCALE Client
=============

As part of our partnership with the Community Seismic Network (CSN) project at Caltech, we borrowed some of their Phidget accelerometers to use with our SCALE devices for seismic monitoring.  They basically monitor background shaking and report a *pick* when the current level is significantly higher than it has been recently.  This pick message is sent to their cloud server using HTTP where the picks from a region are aggregated and analyzed to detect a possible earthquake.

Our integration is basically a huge hack: using a modified `/etc/hosts` file, we trick the CSN client daemon into reporting its picks to `localhost(127.0.0.1)`.  We run a stripped-down version of their server with none of the earthquake-analysis logic that receives the pick and passes it as a SensedEvent into the SCALE client for internal publishing.  In this manner, we're basically using their local event-detection algorithm completely unmodified and running that data through our IoT system.  The client daemon is available in the `csn_bin` folder at the root of this repo.

Please note that we are not supporting this integration for use outside of UCI: the Phidget accelerometers they lent us have a special modification and so likely cannot be purchased at this point.  Instead, we plan to add a `seismic_sensor` module that will run a different picking algorithm for use by others and also comparison between the two.