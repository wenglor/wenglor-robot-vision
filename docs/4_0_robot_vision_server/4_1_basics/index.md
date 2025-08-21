# 4.1 Basics with Robot Server

The calibration process is different, if the camera is mounted on the robot or not on the robot.
Buy one of the calibration plates ZVZJ (see [wenglor website](https://www.wenglor.com/en/) -> ZVZJ) or print the PDF on a stiff and flat material (see [wenglor website](https://www.wenglor.com/en/) -> ZVZJ). For best accuracy, use the wenglor calibration plates ZVZJ.

> **NOTE**
>
> - In case of printing, make sure to print the PDFs at actual size.
> - Typically, the reprojection error for the ZVZJ calibration plate is five times smaller compared to the printed version.
> - For direct light applications, non-transparent calibration plates made of carbon fiber are available. For backlight applications, transparent calibration plates with the material glass are available.
> - The calibration plate should cover at least half of the image and should be visible completely by the camera if possible for most accurate results.

Consider the following points when setting the calibration poses:

- Check that the camera sees the calibration plate when setting the poses.
- Make sure that the difference between one pose and the next one is as big as possible for best accurate results. The same pose could be used several times if not consecutive (e.g. pose one and three can be similar). If space is limited in the application, small differences between one pose and the next one are also possible, but result in less accurate results.
- The calibration plate should cover as much as possible of the camera image and should be visible completely if possible for most accurate results.
