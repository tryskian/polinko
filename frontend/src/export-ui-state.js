export function createExportUiState({ getActiveChatId, setButtonsDisabled }) {
  let inFlight = false;

  function sync() {
    setButtonsDisabled(!getActiveChatId() || inFlight);
  }

  async function runLocked(task) {
    if (inFlight || !getActiveChatId()) {
      sync();
      return false;
    }
    inFlight = true;
    sync();
    try {
      await task();
      return true;
    } finally {
      inFlight = false;
      sync();
    }
  }

  return {
    isInFlight: () => inFlight,
    runLocked,
    sync,
  };
}
