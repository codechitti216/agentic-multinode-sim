from service_template import MicroserviceTemplate
import threading

if __name__ == "__main__":
    service = MicroserviceTemplate("service_d", 8004, ["service_a"])
    service.run_background_tasks()
    service.start()
