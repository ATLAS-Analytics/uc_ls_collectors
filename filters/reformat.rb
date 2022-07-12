

def filter(event)
    readout = event.get("[counters]")
    if readout
        readout.each { |k, v|
            event.set("[#{k}]", v["value"])
        }
    end

    return [event]
end