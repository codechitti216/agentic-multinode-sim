from service_template import MicroserviceTemplate
import threading

if __name__ == "__main__":
    service = MicroserviceTemplate("service_e", 8005, ["service_b", "service_c"])
    service.run_background_tasks()
    service.start()
