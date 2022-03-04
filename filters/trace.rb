def filter(event)
    hs = event.get('[result][paths]').first()
    c = 1
    hops = []
    ttls = []
    asns = []
    rtts = []
    hs.each do |h|
        ttls.push(c)
        c = c + 1
        if h.length > 0
            hops.push(h["ip"])
            asns.push(h["as"]["number"])
            rtts.push(h["rtt"][2,6].to_f)
        else
            hops.push("-")
            asns.push(0)
            rtts.push(0)
        end
    end
    event.set('hops', hops)
    event.set('ttls', ttls)
    event.set('asns', asns)
    event.set('rtts', rtts)
    return [event]
end