import os
import time
from enum import Enum

import adsk.cam
import adsk.core


class AdskWorkspaceType(Enum):
    Design = "Design"
    Manufacture = "CAMEnvironment"

def showError(ui: adsk.core.UserInterface, msg: str):
    if ui:
        ui.messageBox(msg, "Error",
            adsk.core.MessageBoxButtonTypes.OKButtonType,
            adsk.core.MessageBoxIconTypes.CriticalIconType)

def showWarning(ui: adsk.core.UserInterface, msg: str):
    if ui:
        ui.messageBox(msg, "Warning",
            adsk.core.MessageBoxButtonTypes.OKButtonType,
            adsk.core.MessageBoxIconTypes.WarningIconType)

def activateWorkspace(ui: adsk.core.UserInterface, workspace_name: AdskWorkspaceType):
    """
    Prompt user with an option to switch to the CAM workspace if it's not already active.

    ui : UserInterface instance.
    """
    if ui.activeWorkspace.name != workspace_name.name:
        ws = ui.workspaces.itemById(workspace_name.value)
        if not ws:
            showError(ui, "Invalid workspace_name '{}'".format(workspace_name.name))
            return

        answer = ui.messageBox("Activate the {} Workspace?".format(workspace_name.name),
            "Activate Workspace",
            adsk.core.MessageBoxButtonTypes.YesNoButtonType,
            adsk.core.MessageBoxIconTypes.QuestionIconType)

        if answer == adsk.core.DialogResults.DialogYes:
            ws.activate()
