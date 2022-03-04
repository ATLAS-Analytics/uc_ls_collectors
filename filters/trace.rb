def filter(event)
    hs = event.get('[result][paths]').first()
    c = 1
    hops = []
    ttls = []
    asns = []
    rtts = []
    hs.each do |h|
        if h.length > 0
            hops.push(h["ip"])
            rtts.push(h["rtt"][2,6].to_f * 1000)
            ttls.push(c)
            if h["as"]
                asns.push(h["as"]["number"])
            else
                asns.push(0)
            end
        end
        c = c + 1
    end
    event.set('hops', hops)
    event.set('ttls', ttls)
    event.set('asns', asns)
    event.set('rtts', rtts)
    return [event]
end