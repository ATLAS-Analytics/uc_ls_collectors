class Percentile
  attr_reader :key, :value, :k, :is_calculated

  def initialize(quantile, sample_size)
    @key = quantile == 50 ? "delay_median" : "delay_#{quantile}th_percentile"
    @k = (quantile / 100.0) * sample_size
    @value = nil
    @is_calculated = false
  end

  def findvalue(curr_count, hist_value)
    return if @is_calculated
    if curr_count >= @k
      @value = hist_value.to_f
      @is_calculated = true
    end
  end
end

def filter(event)
  unsorted_owds = event.get("result")["histogram-latency"]
  unless unsorted_owds
    event.tag("_missing_histogram_latency")
    return [event]
  end

  owds = Hash[unsorted_owds.sort]
  c = 0
  sum = 0
  owds.each do |key, value|
    kv = key.to_f
    c += value.to_i
    sum += kv * value.to_i
  end

  if c > 0
    mean = sum / c
    variance = 0
    # adding variance and standard deviation
    owds.each do |key, value|
      variance += value.to_i * (key.to_f - mean) ** 2
    end
    variance /= c
    stddev = Math.sqrt(variance)

    # adding the calculation of quantiles
    quantiles = [25, 50, 75, 95]
    percentiles = quantiles.map { |q| Percentile.new(q, c) }
    percentile = percentiles.shift
    curr_count = 0

    owds.sort.each do |key, value|
      hist_value = key.to_f
      curr_count += value.to_i
      # percentiles
      while percentile && curr_count >= percentile.k
        percentile.findvalue(curr_count, hist_value)
        if percentile.is_calculated
          event.set(percentile.key, percentile.value)
          percentile = percentiles.shift
        end
      end
    end

  else
    mean = 0
    stddev = 0
    variance = 0
  end

  # saving other statistics
  event.set("delay_mean", mean)
  event.set("delay_sd", stddev)
  event.set("delay_variance", variance)

  [event]
rescue => e
  event.tag("_rubyexception")
  event.set("[@metadata][filter_error]", e.message)
  event.set("[@metadata][filter_backtrace]", e.backtrace.join("\n"))
  [event]
end
