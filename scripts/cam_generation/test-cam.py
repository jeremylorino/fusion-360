import os
import time
import traceback
from enum import Enum

import adsk.cam
import adsk.core

from . import utils


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.activeDocument
        products = doc.products

        # Get the CAM product
        product = products.itemByProductType("CAMProductType")

        # Check if the document has a CAMProductType. It will not if there are no CAM operations in it.
        if product == None:
            utils.helpers.showError(ui, "There are no CAM operations in the active document")
            return

        # Cast the CAM product to a CAM object (a subtype of product).
        cam = adsk.cam.CAM.cast(product)

        # Check if the template exists (from the path specified above). Show an error if it doesn't exist.
        if cam.setups.count <= 0:
            utils.helpers.showError(ui, "There are no CAM setups in the active document")
            return

        # List of all setups
        setups = cam.setups

        # Specify the full filename of the template.
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        templateFilename = os.path.join(template_path, "face.f3dhsm-template")

        # Check if the template exists (from the path specified above). Show an error if it doesn't exist.
        if not os.path.exists(templateFilename):
            utils.helpers.showError(ui, "The template '{}' does not exist".format(templateFilename))
            return

        # Go through each setup in the document
        for _setup in setups:
            setup = adsk.cam.Setup.cast(_setup)
            # Add the template to each setup.
            results = setup.createFromTemplate(templateFilename)

            # Get the operation that was created. What's created will
            # vary depending on what's defined in the template so you
            # may need more logic to find the result you want.
            operation = adsk.cam.Operation.cast(results.item(0))

            # Change the operation name
            # operation.name = "API added operation"

        # Generate all toolpaths, skipping any that are already valid
        future = cam.generateAllToolpaths(True)
        numOps = future.numberOfOperations

        #  create and show the progress dialog while the toolpaths are being generated.
        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = False
        progress.show("Toolpath Generation Progress", "Generating Toolpaths", 0, 10)

        # Enter a loop to wait while the toolpaths are being generated and update
        # the progress dialog.
        while not future.isGenerationCompleted:
            # since toolpaths are calculated in parallel, loop the progress bar while the toolpaths
            # are being generated but none are yet complete.
            n = 0
            start = time.time()
            while future.numberOfCompleted == 0:
                if time.time() - start > .125: # increment the progess value every .125 seconds.
                    start = time.time()
                    n +=1
                    progress.progressValue = n
                    adsk.doEvents()
                if n > 10:
                    n = 0

            # The first toolpath has finished computing so now display better
            # information in the progress dialog.

            # set the progress bar value to the number of completed toolpaths
            progress.progressValue = future.numberOfCompleted

            # set the progress bar max to the number of operations to be completed.
            progress.maximumValue = numOps

            # set the message for the progress dialog to track the progress value and the total number of operations to be completed.
            progress.message = "Generating %v of %m Toolpaths"
            adsk.doEvents()

        progress.hide()

        utils.helpers.activateWorkspace(ui, utils.helpers.AdskWorkspaceType.Manufacture)

    except:
        utils.helpers.showError(ui, "Failed:\n{}".format(traceback.format_exc()))
