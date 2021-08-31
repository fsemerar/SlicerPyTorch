import qt
import logging

import slicer
from slicer.ScriptedLoadableModule import (
  ScriptedLoadableModule,
  ScriptedLoadableModuleWidget,
  ScriptedLoadableModuleLogic,
  ScriptedLoadableModuleTest,
)


class PyTorchUtils(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "PyTorch Utils"
    self.parent.categories = ['Utilities']
    self.parent.dependencies = []
    self.parent.contributors = ["Fernando Perez-Garcia (University College London)"]
    self.parent.helpText = 'This hidden module containing some tools to work with PyTorch inside Slicer.'
    self.parent.acknowledgementText = (
      'This work was funded by the Engineering and Physical Sciences'
      ' Research Council (EPSRC) and supported by the UCL Centre for Doctoral'
      ' Training in Intelligent, Integrated Imaging in Healthcare, the UCL'
      ' Wellcome / EPSRC Centre for Interventional and Surgical Sciences (WEISS),'
      ' and the School of Biomedical Engineering & Imaging Sciences (BMEIS)'
      " of King's College London."
    )


class PyTorchUtilsWidget(ScriptedLoadableModuleWidget):
  def setup(self):
    super().setup()
    self.installPushButton = qt.QPushButton('Install PyTorch')
    self.layout.addWidget(self.installPushButton)
    self.installPushButton.clicked.connect(self.onInstallTorch)
    self.layout.addStretch(1)

  def onInstallTorch(self):
    torch = PyTorchUtilsLogic().torch
    slicer.util.delayDisplay(f'PyTorch {torch.__version__} installed correctly')


class PyTorchUtilsLogic(ScriptedLoadableModuleLogic):
  def __init__(self):
    self._torch = None

  @property
  def cuda(self):
    """Return True if a CUDA-compatible device is available."""
    return self.getDevice() != 'cpu'

  @property
  def torch(self):
    """``torch`` Python module. it will be installed if necessary."""
    if self._torch is None:
      logging.info('Importing torch...')
      self._torch = self.importTorch()
    return self._torch

  def importTorch(self):
    """Import the ``torch`` Python module, installing it if necessary."""
    try:
      import torch
    except ModuleNotFoundError:
      torch = self.installTorch()
    logging.info(f'PyTorch {torch.__version__} imported correctly')
    logging.info(f'CUDA available: {torch.cuda.is_available()}')
    return torch

  def installTorch(self):
    """Install PyTorch and return the ``torch`` Python module."""
    wheelUrl = self.getTorchUrl()
    slicer.util.pip_install(wheelUrl)
    import torch
    logging.info(f'PyTorch {torch.__version__} installed correctly')
    return torch

  @staticmethod
  def getTorchUrl():
    """Get best PyTorch version compatible with the device.

    This method uses ``light-the-torch`` to get the most recent version of
    PyTorch compatible with the installed NVIDIA drivers. If no CUDA-compatible
    device is found, a version compiled for CPU will be installed.
    """
    slicer.util.pip_install('light-the-torch')
    import light_the_torch as ltt
    wheelUrl = ltt.find_links(['torch'])[0]
    return wheelUrl

  def getPyTorchHubModel(self, repoOwner, repoName, modelName, addPretrainedKwarg=True, *args, **kwargs):
    """Use PyTorch Hub to download a PyTorch model, typically pre-trained.

    More information can be found at https://pytorch.org/hub/.
    """
    repo = f'{repoOwner}/{repoName}'
    if addPretrainedKwarg:
      kwargs['pretrained'] = True
    model = self.torch.hub.load(repo, modelName, *args, **kwargs)
    return model

  def getDevice(self):
    """Get CUDA device if available and CPU otherwise."""
    return self.torch.device('cuda') if self.torch.cuda.is_available() else 'cpu'


class PyTorchUtilsTest(ScriptedLoadableModuleTest):

  def tearDown(self):
    self.landmarksPath.unlink()

  def runTest(self):
    self.test_PyTorchUtils()

  def _delayDisplay(self, message):
    if not slicer.app.testingEnabled():
      self.delayDisplay(message)

  def test_PyTorchUtils(self):
    self._delayDisplay('Starting the test')
    logic = PyTorchUtilsLogic()
    self._delayDisplay(f'CUDA available: {logic.torch.cuda.is_available()}')
    self._delayDisplay('Test passed!')
