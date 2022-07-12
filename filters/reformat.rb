

def filter(event)
    readout = event.get("[counters]")
    if readout
        readout.each { |k, v|
            event.set("[#{k}]", v.value)
        }
    end

    # event.set("src", get_ips(event.get("src_host")) ) unless event.get("src")
    # event.set("dest", get_ips(event.get("dest_host"))) unless event.get("dest")

    return [event]
end